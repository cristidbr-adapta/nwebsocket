<a id="nwebsocket"></a>

# nwebsocket

WebSocket client without async.

<a id="nwebsocket.WebSocket"></a>

## WebSocket Objects

```python
class WebSocket(object)
``` 

WebSocket for Python without async

<a id="nwebsocket.WebSocket.__init__"></a>

#### \_\_init\_\_

```python
def __init__(url, options=None)
```

Constructs a new ``WebSocket`` client.

**Arguments**:

- `url` (`string`): WebSocket URL to connect to, must start with ws: or wss:
- `options` (`dict(maxPayload=1024*1024)`): Socket options, maxPayload represents maximum message size in bytes

<a id="nwebsocket.WebSocket.onopen"></a>

#### onopen

```python
def onopen()
```

Callback for socket opened, fires after handshake is completed

<a id="nwebsocket.WebSocket.onclose"></a>

#### onclose

```python
def onclose()
```

Callback for socket closed, fires upon disconnection

<a id="nwebsocket.WebSocket.onerror"></a>

#### onerror

```python
def onerror(error)
```

Callback for socket error

**Arguments**:

- `error` (`string`): Error message

<a id="nwebsocket.WebSocket.onmessage"></a>

#### onmessage

```python
def onmessage(message)
```

Callback for message received

**Arguments**:

- `message` (`string/bytes`): Data received from the server

<a id="nwebsocket.WebSocket.send"></a>

#### send

```python
def send(message)
```

Sends message to the server

**Arguments**:

- `message` (`string/bytes`): Data to send, can be either string or binary

**Raises**:

- `ConnectionError`: if the connection is not yet established or was closed

<a id="nwebsocket.WebSocket.close"></a>

#### close

```python
def close()
```

Closes the socket and blocks until the closing is acknowledged

