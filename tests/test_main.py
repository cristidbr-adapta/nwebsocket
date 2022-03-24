# test_main.py

import pytest

import time 

from nwebsocket import WebSocket 

def test_connect_echo():
    sock = WebSocket( 'wss://ws.postman-echo.com/raw' ) 

    # can connect
    assert sock.readyState == WebSocket.CONNECTING
    
    # flags check
    open_flag = False 
    rx_messages = []

    def handle_open():
        nonlocal open_flag
        open_flag = True
    
    def handle_close():
        nonlocal open_flag
        open_flag = False 

    def handle_error():
        nonlocal open_flag
        open_flag = False 

    def handle_message( m ):
        rx_messages.append( m )

    sock.onopen = handle_open
    sock.onerror = handle_error
    sock.onclose = handle_close
    sock.onmessage = handle_message

    # has connected
    timeout = time.time() + 10.
    while( time.time() < timeout and sock.readyState == WebSocket.CONNECTING ):
        time.sleep( 1e-4 )

    assert sock.readyState == WebSocket.OPEN
    assert open_flag == True 

    # close connection
    sock.close()

    time.sleep( 1. )
    assert sock.readyState == WebSocket.CLOSED
    