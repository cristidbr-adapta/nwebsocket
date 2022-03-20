import time
import curio 
import threading

from urllib.parse import urlparse
from curio import Queue, UniversalQueue, spawn, TaskGroup
from curio.socket import IPPROTO_TCP, TCP_NODELAY

from wsproto import WSConnection, ConnectionType
from wsproto.events import (
    AcceptConnection,
    CloseConnection,
    RejectConnection,
    Message,
    Ping,
    Pong,
    Request,
    TextMessage,
)

def uriparse( uri, default_port = 8080 ):
    info = urlparse( uri )
    host = info.netloc.split( ':' )[ 0 ]
    path = info.path 

    try: 
        port = int( info.netloc.split( ':' )[ -1 ] )
    except:
        port = default_port
    
    return dict( port = port, path = path, host = host )


"""
Manages RX/TX events on the WebSocket using curio.Queue
"""
async def ws_events_manage( rx_queue, tx_queue, endpoint, socket ):
    # disable nagle
    socket.setsockopt( IPPROTO_TCP, TCP_NODELAY, 1 )
    
    # client parser
    wscn = WSConnection( ConnectionType.CLIENT )
    closed = False
    
    # form handshake
    handshake = wscn.send( Request( host = '{}:{}'.format( endpoint[ 'host' ], endpoint[ 'port' ] ), target = endpoint[ 'path' ] ) )
    await socket.sendall( handshake )
    
    # catch and close connection
    async def manage_rx( socket, blen ):
        try:
            return await socket.recv( blen )
        except:
            return None

    # closed flag
    while not closed:
        rx_task = await spawn( manage_rx, socket, 65535 )
        tx_task = await spawn( tx_queue.get )
        
        # execute both
        async with TaskGroup( [ rx_task, tx_task ] ) as g:
            task = await g.next_done()
            result = await task.join()
            await g.cancel_remaining()
            
        # rx yielded
        if task is rx_task:
            # parse data
            wscn.receive_data( result )

            for event in wscn.events():
                # accepted
                if isinstance( event, AcceptConnection ):
                    await rx_queue.put( event )
                
                # receive message
                elif isinstance( event, TextMessage ):
                    await rx_queue.put( event.data )
                    
                # handle closures
                elif isinstance( event, CloseConnection ):
                    await rx_queue.put( event )
                    await rx_queue.put( None )
        
                # handle pong
                elif isinstance( event, Pong ):
                    pass 
                          
                # handle ping
                elif isinstance( event, Ping ):
                    try:
                        await socket.sendall( wscn.send( Pong() ) )
                    except:
                        await tx_queue.put( None )
                
                else:
                    raise Exception( "Do not know how to handle event: " + str( event ) )
        
        # tx yielded
        else:
            # terminate at None from tx_queue
            if result is None:
                await wscn.close()
                closed = True
            else:
                try:
                    await socket.sendall( wscn.send( Message( result ) ) )
                except:
                    await tx_queue.put( None )

""" 
Manage socket connection
"""
async def ws_socket_manage( rx_queue, tx_queue, uri, callback ):
    endpoint = uriparse( uri )
    
    # let tx_queue be nonlocal and sleep
    send = lambda m: tx_queue.put( m ) and time.sleep( 0.001 )
    
    # open socket connection
    try:
        socket = await curio.open_connection( endpoint[ 'host' ], endpoint[ 'port' ], ssl = False )
    except:
        callback( RejectConnection( 400 ), send )
        return None    
    
    # loop 
    async with socket:
        ws_task = await spawn( ws_events_manage, rx_queue, tx_queue, endpoint, socket )
            
        while True:
            # attempt to read incoming messages
            message = await rx_queue.get()
        
            # terminate
            if message is None:
                break
            
            # fire callback and collect messages
            callback( message, send )


class WebSocket( object ):
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3
    
    """ 
    WebSocket for Python
    """
    def __init__( self, uri, detach = True ):
        self.uri = uri
        self.detach = detach
        self.readyState = WebSocket.CONNECTING
        
        # callbacks
        self.onopen = lambda: None 
        self.onclose = lambda: None
        self.onerror = lambda: None
        self.onmessage = lambda: None
        
        self._send = None

        # create event queues
        self.rx_queue = Queue()
        self.tx_queue = UniversalQueue()
        
        # create detachable async context
        def detach( f ):
            def wrap( *args ):
                thr = threading.Thread( target = f, args = args )
                thr.daemon = True
                thr.start()
                return thr 
            
            return wrap
        
        async_detached = detach( curio.run )
        
        # create thread
        self.manage = ws_socket_manage( 
            self.rx_queue, 
            self.tx_queue, 
            self.uri,
            lambda m, s: self.handleRXEvent( m, s ) 
        )
        
        if( self.detach ): 
            self.task = async_detached( self.manage )
    
    def send( self, message ):
        if( self._send is None ):
            raise RuntimeError( 'WebSocket not connected' ) 
        else:
            self._send( message )
            time.sleep( 0.002 )
    
    def join( self ):
        if self.detach: 
            return None
    
        return curio.run( self.manage )
    
    def handleRXEvent( self, message, send ):
        self._send = send

        # fire onopen 
        if isinstance( message, AcceptConnection ):
            self.readyState = WebSocket.OPEN
            self.onopen()
        
        # errored out
        elif isinstance( message, RejectConnection ):
            self.readyState = WebSocket.CLOSED
            self.onerror( message )
            
        # closed out
        elif isinstance( message, CloseConnection ):
            self.readyState = WebSocket.CLOSED
            self.onclose( message )
        
        # message 
        elif isinstance( message, str ):
            self.onmessage( message )
