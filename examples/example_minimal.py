import time 

# example_minimal.py
from nwebsocket import WebSocket 

wscn = WebSocket( "wss://ws.postman-echo.com/raw" )

wscn.onmessage = lambda m: print( m )
wscn.onopen = lambda: print( "Opened connection" )
wscn.onclose = lambda: print( "Closed connection" )
wscn.onerror = lambda: print( "Connection errored out" )

print( wscn.readyState )

wscn.send( 'text' )

time.sleep( 5. )
