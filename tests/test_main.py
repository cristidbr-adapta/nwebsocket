# test_main.py

import pytest

import time 

from nwebsocket import WebSocket 

def test_connect_echo():
    sock = WebSocket( 'wss://ws.postman-echo.com/raw' ) 

    # can connect
    assert sock.readyState == WebSocket.CONNECTING
    
    # flags check
    class Tracker:
        def __init__( self, wscn ):
            self.open = False 
            self.error = False 
            self.messages = []

            self.wscn = wscn
            self.wscn.onopen = self.handle_open
            self.wscn.onclose = self.handle_close
            self.wscn.onmessage = self.handle_message
            self.wscn.onerror = self.handle_error

        def handle_open( self ):
            self.open = True 

        def handle_close( self ):
            self.open = False

        def handle_error( self ):
            self.open = False
            self.error = True 

        def handle_message( self, m ):
            self.messages.append( m )

    wst = Tracker( sock )

    # has connected
    timeout = time.time() + 10.
    while( time.time() < timeout and sock.readyState == WebSocket.CONNECTING ):
        time.sleep( 1e-4 )

    assert sock.readyState == WebSocket.OPEN
    assert wst.open == True 

    # close connection
    sock.close()
    assert sock.readyState == WebSocket.CLOSED
    assert wst.open == False 

    