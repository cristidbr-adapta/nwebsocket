# example_class.py
import time

from nwebsocket import WebSocket

class WSProtocol(WebSocket):
    def __init__(self,url):
        super.__init__(url)

        self.messages = []

    def onopen(self):
        print("Opened connection")

    def onclose(self):
        print("Closed connection")

    def onerror(self):
        print("Connection errored out")

    def onmessage(self, m):
        self.messages.append(m)

wscn = WSProtocol("wss://ws.postman-echo.com/raw")

while(not wscn.readyState):
    time.sleep(1e-4)

wscn.send('text')
time.sleep(1.)

print(wscn.messages)

wscn.close()
