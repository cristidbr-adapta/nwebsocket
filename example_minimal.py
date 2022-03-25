import time

# example_minimal.py
import nwebsocket

wscn = nwebsocket.WebSocket("wss://ws.postman-echo.com/raw")

wscn.onmessage = lambda m: print(m)
wscn.onopen = lambda: print("Opened connection")
wscn.onclose = lambda: print("Closed connection")
wscn.onerror = lambda: print("Connection errored out")

while(not wscn.readyState):
    time.sleep(1e-4)

wscn.send('text')

time.sleep(2.)

wscn.close()
