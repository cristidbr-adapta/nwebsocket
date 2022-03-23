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

__version__ = "0.9.0"

class WebSocket(object):
    """
    WebSocket for Python
    """

    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3

    def __init__(self, uri, detach=True):
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
            lambda m, s: self.handleRXEvent(m, s)
        )

        if(self.detach):
            self.task = async_detached(self.manage)

    def send(self, message):
        if(self._send is None):
            raise RuntimeError('WebSocket not connected')
        else:
            self._send(message)
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
            self.onclose(message)

        # message
        elif isinstance(message, str):
            self.onmessage(message)
