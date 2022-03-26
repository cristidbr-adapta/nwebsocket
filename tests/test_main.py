# test_main.py

import pytest

import time
import random
import string

from nwebsocket import WebSocket

from wsproto.events import (
    Ping,
)

from .server import echo_server

@pytest.fixture(scope='session')
def server():
    server = echo_server(8001)
    yield server


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

# flags check
class Tracker:
    def __init__(self, wscn):
        self.open = False
        self.error = False
        self.messages = []

        self.wscn = wscn
        self.wscn.onopen = self.handle_open
        self.wscn.onclose = self.handle_close
        self.wscn.onmessage = self.handle_message
        self.wscn.onerror = self.handle_error

    def handle_open(self):
        self.open = True

    def handle_close(self):
        self.open = False

    def handle_error(self):
        self.open = False
        self.error = True

    def handle_message(self, m):
        self.messages.append(m)


def test_unable_to_connect(server):
    sock = WebSocket('ws://noconnect')

    while(not sock.readyState):
        time.sleep(1e-4)

    assert sock.readyState == WebSocket.CLOSED


def test_send_raise(server):
    raised = False
    sock = WebSocket('wss://ws.postman-echo.com/raw')

    try:
        sock.send('should_fail')
    except RuntimeError:
        raised = True

    assert raised == True


def test_messaging_echo_secure(server):
    sock = WebSocket('wss://ws.postman-echo.com/raw')

    # can connect
    assert sock.readyState == WebSocket.CONNECTING

    wst = Tracker(sock)

    # has connected
    timeout = time.time() + 10.
    while(time.time() < timeout and sock.readyState == WebSocket.CONNECTING):
        time.sleep(1e-4)

    assert sock.readyState == WebSocket.OPEN
    assert wst.open == True

    # send ping message
    sock.send(Ping())

    # send small text and verify echo
    wst.messages = []
    sock.send('test_0')

    limit = time.time() + 5.
    while(len(wst.messages) == 0 and time.time() < limit):
        time.sleep(1e-4)

    assert len(wst.messages) == 1
    assert wst.messages[0] == 'test_0'

    # send multipart text message and verify echo
    multipart_text = random_string(65536)

    wst.messages = []
    sock.send(multipart_text)

    limit = time.time() + 5.
    while(len(wst.messages) == 0 and time.time() < limit):
        time.sleep(1e-4)

    assert len(wst.messages) == 1
    assert wst.messages[0] == multipart_text

    # close connection
    sock.close()
    assert sock.readyState == WebSocket.CLOSED
    assert wst.open == False



def test_messaging_echo_binary(server):
    sock = WebSocket('ws://localhost:8001/')

    wst = Tracker(sock)

    # has connected
    timeout = time.time() + 10.
    while(time.time() < timeout and sock.readyState == WebSocket.CONNECTING):
        time.sleep(1e-4)

    assert sock.readyState == WebSocket.OPEN
    assert wst.open == True

    # send small text and verify echo
    wst.messages = []
    sock.send(bytes('test_0'.encode('utf-8')))

    limit = time.time() + 5.
    while(len(wst.messages) == 0 and time.time() < limit):
        time.sleep(1e-4)

    assert len(wst.messages) == 1
    assert wst.messages[0] == bytes('test_0'.encode('utf-8'))

    # send multipart binary message and verify echo
    multipart_binary = bytes(random_string(65536).encode('utf-8'))

    wst.messages = []
    sock.send(multipart_binary)

    limit = time.time() + 5.
    while(len(wst.messages) == 0 and time.time() < limit):
        time.sleep(1e-4)

    time.sleep(5.)
    assert len(wst.messages) == 1
    assert wst.messages[0] == multipart_binary

    # close connection
    sock.close()
    assert sock.readyState == WebSocket.CLOSED
    assert wst.open == False


