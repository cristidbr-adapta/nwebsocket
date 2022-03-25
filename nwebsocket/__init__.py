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

__version__ = '0.9.3'


class WebSocket(object):
    """
    WebSocket for Python without async
    """

    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3

    def __init__(self, uri, detach=True):
        self.uri = uri
        self.detach = detach
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
            self.uri,
            lambda m, s: self.handleRXEvent(m, s),
        )

        if(self.detach):
            self.task = async_detached(self.manage)

    def onopen(self):
        pass

    def onclose(self):
        pass

    def onerror(self, error):
        pass

    def onmessage(self, message):
        pass

    def send(self, message):
        if(self._send is None):
            raise RuntimeError('WebSocket not connected')
        else:
            self._send(message)
            time.sleep(1e-5)

    def close(self):
        self.tx_queue.put(CloseConnection(0))
        self.tx_queue.put(None)
        while(self.readyState != WebSocket.CLOSED):
            time.sleep(1e-5)

    def join(self):
        if self.detach:
            return None

        return curio.run(self.manage)

    def handleRXEvent(self, message, send):
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
        elif isinstance(message, tuple):
            chunk, complete = message

            if self.buffer is None:
                self.buffer = chunk
            else:
                self.buffer += chunk

            if complete:
                self.onmessage(self.buffer)
                self.buffer = None
