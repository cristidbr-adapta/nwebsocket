# test_main.py

import pytest

import time 

from nwebsocket import WebSocket 

def test_connect():
    sock = WebSocket( 'wss://ws.postman-echo.com/raw' ) 

    # can connect
    assert sock.readyState == WebSocket.CONNECTING
    
    # flags check
    open_flag = False 
    rx_messages = []

    def handle_open():
        open_flag = True
    
    def handle_close():
        open_flag = False 

    def handle_error():
        open_flag = False 

    def handle_message( m ):
        rx_messages.append( m )

    sock.onopen = handle_open
    sock.onerror = handle_error
    sock.onclose = handle_close

    # has connected
    timeout = time.time() + 10.
    while( time.time() < timeout and sock.readyState == WebSocket.CONNECTING ):
        time.sleep( 1e-4 )

    assert sock.readyState == WebSocket.OPEN

    # message echo
