"""A Curio websocket server.

pip install wsproto before running this.

"""
from curio import Queue, run, spawn, TaskGroup
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
        wstask = await spawn(manage_rx, client, 65535)
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
                    await in_q.put(event.data)
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
                await client.sendall(wsconn.send(Message(result)))

    print("Bridge done.")


async def ws_echo_server(in_queue, out_queue):
    """Just echo websocket messages, reversed. Echo 3 times, then close."""
    while True:
        msg = await in_queue.get()
        if msg is None:
            # The ws connection was closed.
            break
        await out_queue.put(msg)
    print("Handler done.")


def serve_ws(handler):
    """Start processing web socket messages using the given handler."""
    async def run_ws(client, addr):
        in_q, out_q = Queue(), Queue()
        ws_task = await spawn(ws_adapter, in_q, out_q, client, addr)
        await handler(in_q, out_q)
        await out_q.put(None)
        await ws_task.join()  # Wait until it's done.
        # Curio will close the socket for us after we drop off here.
        print("Master task done.")

    return run_ws


if __name__ == '__main__':
    from curio import tcp_server
    port = 8001
    print(f'Listening on port {port}.')
    run(tcp_server, '', port, serve_ws(ws_echo_server))
