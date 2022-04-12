"""
nwebsocket
~~~~~~~~~~

WebSocket client without async.
"""

import time
import curio
import threading

from curio import Queue, UniversalQueue

from wsproto.events import (
    AcceptConnection,
    CloseConnection,
    RejectConnection,
)

from .events import ws_socket_manage

__version__ = '1.0.0'


class WebSocket(object):
    """
    WebSocket for Python without async
    """

    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3

    def __init__(self, url, options=None):
        """
        Constructs a new ``WebSocket`` client.

        :param url: WebSocket URL to connect to, must start with ws: or wss:
        :type url: string 

        :param options: Socket options, maxPayload represents maximum message size in bytes
        :type options: dict(maxPayload=1024*1024) 
        """
        self.url = url
        self.options = dict(maxPayload=int(1024*1024)
                            ) if (options is None) else options
        self.readyState = WebSocket.CONNECTING

        self._send = None

        # create event queues
        self.rx_queue = Queue()
        self.tx_queue = UniversalQueue()

        # buffer chunks
        self.buffer = None

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
        self.manage = ws_socket_manage(
            self.rx_queue,
            self.tx_queue,
            self.url,
            lambda m, s: self._handleRXEvent(m, s),
            self.options
        )

        self.task = async_detached(self.manage)

    def __str__(self):
        return "<WebSocket url={} readyState={}>".format(self.url, self.readyState)

    def __repr__(self):
        return self.__str__()

    def onopen(self):
        """
        Callback for socket opened, fires after handshake is completed
        """
        pass

    def onclose(self):
        """
        Callback for socket closed, fires upon disconnection
        """
        pass

    def onerror(self, error):
        """
        Callback for socket error

        :param error: Error message
        :type error: string 
        """
        pass

    def onmessage(self, message):
        """
        Callback for message received

        :param message: Data received from the server
        :type message: string/bytes
        """
        pass

    def send(self, message):
        """
        Sends message to the server

        :param message: Data to send, can be either string or binary
        :type message: string/bytes

        :raises
            ConnectionError: if the connection is not yet established or was closed
        """
        if(self._send is None):
            raise ConnectionError('WebSocket not connected')
        else:
            self._send(message)
            time.sleep(1e-5)

    def close(self):
        """
        Closes the socket and blocks until the closing is acknowledged
        """
        self.tx_queue.put(CloseConnection(0))
        self.tx_queue.put(None)
        while(self.readyState != WebSocket.CLOSED):
            time.sleep(1e-5)

    def _handleRXEvent(self, message, send):
        self._send = send

        # fire onopen
        if isinstance(message, AcceptConnection):
            self.readyState = WebSocket.OPEN
            self.onopen()

        # errored out
        elif isinstance(message, RejectConnection):
            self.readyState = WebSocket.CLOSED
            self.onerror(message)

        # closed out
        elif isinstance(message, CloseConnection):
            self.readyState = WebSocket.CLOSED
            self.onclose()

        # message
        elif isinstance(message, tuple) and len(message) == 2:
            chunk, complete = message

            if self.buffer is None:
                self.buffer = chunk
            else:
                self.buffer += chunk

            if complete:
                self.onmessage(self.buffer)
                self.buffer = None
