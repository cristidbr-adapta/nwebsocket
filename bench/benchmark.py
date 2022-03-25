import time

from nwebsocket import WebSocket

wscn = WebSocket('ws://localhost:8001/')

time.sleep(1.)

wscn.send('test')

print(wscn.readyState)

# throughput test
message_counter = 0


def handle_message(m):
    global message_counter
    message_counter += 1


wscn.onmessage = handle_message

# test one
wscn.send('test_{}'.format(message_counter))

message_counter = 0
limit = time.time() + 1.

while time.time() < limit:
    prev_message_counter = message_counter

    # roundtrip
    wscn.send('test_{}'.format(message_counter))

    while message_counter == prev_message_counter:
        time.sleep(1e-5)

print(message_counter, 'roundtrip messages/second')
