# test_main.py

import pytest

import time 

from nwebsocket import WebSocket 

def test_connect():
    sock = WebSocket( 'ws://ws.postman-echo.com/raw' ) 

    # can connect
    assert sock.readyState == WebSocket.CONNECTING
    
    sock.onopen = lambda: print( 'OPENED' )
    sock.onerror = lambda: print( 'ERROR' )

    # has connected
    time.sleep( 20. )
    print( sock.readyState )
    assert sock.readyState == WebSocket.OPEN
