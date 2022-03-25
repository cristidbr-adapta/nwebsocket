# example_class.py
import time

from nwebsocket import WebSocket


class WSProtocolLogic(WebSocket):
    def __init__(self, url):
        super().__init__(url)

        self.messages = []

        # wait for connection, close or error
        while(not self.readyState):
            time.sleep(1e-4)

    def onopen(self):
        print("Opened connection")

    def onclose(self):
        print("Closed connection")

    def onerror(self, e):
        print("Connection error", e)

    def onmessage(self, m):
        self.messages.append(m)


wscn = WSProtocolLogic("wss://ws.postman-echo.com/raw")

wscn.send('text')
time.sleep(1.)

print(wscn.messages)

wscn.close()
