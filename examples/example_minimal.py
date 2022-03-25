# example_minimal.py
import time

from nwebsocket import WebSocket

wscn = WebSocket("wss://ws.postman-echo.com/raw")

wscn.onmessage = lambda m: print(m)
wscn.onopen = lambda: print("Opened connection")
wscn.onclose = lambda: print("Closed connection")
wscn.onerror = lambda e: print("Connection error", e)

while(not wscn.readyState):
    time.sleep(1e-4)

wscn.send('text')
time.sleep(1.)

wscn.close()
