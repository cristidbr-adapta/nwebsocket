"""A Curio websocket server.

pip install wsproto before running this.

"""
from ast import Bytes
import curio 
import threading

from curio import Queue, spawn, TaskGroup
from curio import tcp_server
from curio.socket import IPPROTO_TCP, TCP_NODELAY

from wsproto import WSConnection, ConnectionType
from wsproto.events import (CloseConnection, AcceptConnection, Request,
                            BytesMessage, TextMessage, Message)

DATA_TYPES = (BytesMessage, TextMessage)


async def ws_adapter(in_q, out_q, client, _):
    """A simple, queue-based Curio-Sans-IO websocket bridge."""
    client.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
    wsconn = WSConnection(ConnectionType.SERVER)
    closed = False
    buffer = None

    # catch and close connection
    async def manage_rx(socket, blen):
        try:
            data = await socket.recv(blen)
            if(len(data) == 0):
                return None

            return data
        except:
            return None

    while not closed:
        wstask = await spawn(manage_rx, client, int(1024*1024))
        outqtask = await spawn(out_q.get)

        async with TaskGroup([wstask, outqtask]) as g:
            task = await g.next_done()
            result = await task.join()
            await g.cancel_remaining()

        if task is wstask:
            wsconn.receive_data(result)

            for event in wsconn.events():
                cl = event.__class__
                if cl in DATA_TYPES:
                    await in_q.put((event.data, event.message_finished))
                elif cl is Request:
                    # Auto accept. Maybe consult the handler?
                    await client.sendall(wsconn.send(AcceptConnection()))
                elif cl is CloseConnection:
                    # The client has closed the connection.
                    await in_q.put(None)
                    closed = True
                else:
                    print(event)
        else:
            # We got something from the out queue.
            if result is None:
                # Terminate the connection.
                print("Closing the connection.")
                await client.sendall(wsconn.send(CloseConnection(0)))
                closed = True
            else:
                if(isinstance(result, tuple)):
                    data, complete = result
                    if buffer is None:
                        buffer = data
                    else:
                        buffer += data
                    
                    if complete:
                        m = BytesMessage(buffer) if isinstance(buffer, bytes) else TextMessage(buffer)
                        buffer = None
                        await client.sendall(wsconn.send(m))
                        
async def ws_echo_server(in_queue, out_queue):
    """Just echo websocket messages, reversed. Echo 3 times, then close."""
    while True:
        msg = await in_queue.get()
        if msg is None:
            # The ws connection was closed.
            break
        await out_queue.put(msg)


def serve_ws(handler):
    """Start processing web socket messages using the given handler."""
    async def run_ws(client, addr):
        in_q, out_q = Queue(), Queue()
        ws_task = await spawn(ws_adapter, in_q, out_q, client, addr)
        await handler(in_q, out_q)
        await out_q.put(None)
        await ws_task.join()  # Wait until it's done.

    return run_ws

def echo_server( port = 8001 ):
    print('Listening on port', port)

    # create detachable async context
    def detach(f):
        def wrap(*args):
            thr = threading.Thread(target=f, args=args)
            thr.daemon = True
            thr.start()
            return thr

        return wrap

    async_detached = detach(curio.run)

    # create thread
    task = async_detached(tcp_server( '', port, serve_ws(ws_echo_server)))

    return task

if __name__ == '__main__':
    import time
    echo_server()

    while(True):
        time.sleep(1.)
