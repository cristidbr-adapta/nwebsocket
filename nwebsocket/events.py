"""
nwebsocket/events
~~~~~~~~~~~~~~~~

Event management functions.
"""

import time
import curio

from curio import spawn, TaskGroup
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

from .utils import uriparse


async def ws_events_manage(rx_queue, tx_queue, endpoint, socket):
    """
    Manages RX/TX events on the WebSocket using curio.Queue
    """

    # disable nagle
    socket.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)

    # client parser
    wscn = WSConnection(ConnectionType.CLIENT)
    closed = False

    # form handshake
    handshake = wscn.send(
        Request(
            host='{}:{}'.format(
                endpoint['host'],
                endpoint['port']),
            target=endpoint['path']))
    await socket.sendall(handshake)

    # catch and close connection
    async def manage_rx(socket, blen):
        try:
            return await socket.recv(blen)
        except BaseException:
            return None

    # closed flag
    while not closed:
        rx_task = await spawn(manage_rx, socket, 65535)
        tx_task = await spawn(tx_queue.get)

        # execute both
        async with TaskGroup([rx_task, tx_task]) as g:
            task = await g.next_done()
            result = await task.join()
            await g.cancel_remaining()

        # rx yielded
        if task is rx_task:
            # parse data
            wscn.receive_data(result)

            for event in wscn.events():
                # accepted
                if isinstance(event, AcceptConnection):
                    await rx_queue.put(event)

                # receive message
                elif isinstance(event, TextMessage):
                    await rx_queue.put(event.data)

                # handle closures
                elif isinstance(event, CloseConnection):
                    await rx_queue.put(event)
                    await rx_queue.put(None)

                # handle pong
                elif isinstance(event, Pong):
                    pass

                # handle ping
                elif isinstance(event, Ping):
                    try:
                        await socket.sendall(wscn.send(Pong()))
                    except BaseException:
                        await tx_queue.put(None)

                else:
                    print(
                        "Do not know how to handle event: " + str(event))

        # tx yielded
        else:
            # terminate at None from tx_queue
            if result is None:
                await wscn.close()
                closed = True
            else:
                try:
                    await socket.sendall(wscn.send(Message(result)))
                except BaseException:
                    await tx_queue.put(None)


async def ws_socket_manage(rx_queue, tx_queue, uri, callback):
    """
    Manage socket connection
    """

    endpoint = uriparse(uri)
    secure = ( endpoint['port'] == 443 ) or endpoint.startswith( 'wss:' )

    # let tx_queue be nonlocal and sleep
    def send(m): return tx_queue.put(m) and time.sleep(1e-5)
    
    # open socket connection
    try:
        socket = await curio.open_connection(endpoint['host'], endpoint['port'], ssl=secure )
    except BaseException:
        callback(RejectConnection(400), send)
        return None

    # loop
    async with socket:
        ws_task = await spawn(ws_events_manage, rx_queue, tx_queue, endpoint, socket)

        while True:
            # attempt to read incoming messages
            message = await rx_queue.get()

            # terminate
            if message is None:
                break

            # fire callback and collect messages
            callback(message, send)
