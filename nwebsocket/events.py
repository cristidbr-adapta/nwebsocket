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
    Ping,
    Pong,
    Request,
    TextMessage,
    BytesMessage,
)

from .utils import uriparse


async def ws_events_manage(rx_queue, tx_queue, endpoint, socket, options):
    """
    Manages RX/TX events on the WebSocket using curio.Queue and UniversalQueue
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
            data = await socket.recv(blen)
            if(len(data) == 0):
                return None

            return data
        except:
            return None

    # closed flag
    while not closed:
        rx_task = await spawn(manage_rx, socket, options['maxPayload'])
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
                    await rx_queue.put((event.data, event.message_finished))

                # receive message
                elif isinstance(event, BytesMessage):
                    await rx_queue.put((event.data, event.message_finished))

                # handle closures
                elif isinstance(event, CloseConnection):
                    await rx_queue.put(event)

                    try:
                        await socket.sendall(wscn.send(event.response()))
                    except:
                        pass

                    await tx_queue.put(None)

                    closed = True
                    break

                # handle pong
                elif isinstance(event, Pong):
                    pass

                # handle ping
                elif isinstance(event, Ping):
                    try:
                        await socket.sendall(wscn.send(Pong()))
                    except:
                        await tx_queue.put(None)

        # tx yielded
        else:
            # terminate at None from tx_queue
            if result is None:
                await rx_queue.put(CloseConnection(0))
                closed = True
            else:
                try:
                    m = result

                    if isinstance(result, bytes):
                        m = BytesMessage(result)
                    elif isinstance(result, str):
                        m = TextMessage(result)

                    await socket.sendall(wscn.send(m))
                except:
                    await tx_queue.put(None)

    # close socket and end task
    await socket.close()


async def ws_socket_manage(rx_queue, tx_queue, uri, callback, options):
    """
    Manage socket connection
    """

    endpoint = uriparse(uri)
    secure = endpoint['port'] == 443

    # let tx_queue be nonlocal and sleep
    def send(m): return tx_queue.put(m) and time.sleep(1e-3)

    # open socket connection
    try:
        socket = await curio.open_connection(endpoint['host'], endpoint['port'], ssl=secure)
    except:
        callback(RejectConnection(400), send)
        return None

    # loop
    async with socket:
        ws_task = await spawn(ws_events_manage, rx_queue, tx_queue, endpoint, socket, options)

        while True:
            # attempt to read incoming messages
            message = await rx_queue.get()

            # terminate
            if message is None:
                break

            # fire callback and collect messages
            callback(message, send)

        ws_task.join()

    await socket.close()

    # end gracefully
    callback(CloseConnection(0), send)
