"""
nwebsocket/utils
~~~~~~~~~~~~~~~~

URL Parsing utilities.
"""

from urllib.parse import urlparse


def uriparse(uri, default_port=None):
    info = urlparse(uri)
    host = info.netloc.split(':')[0]
    path = info.path

    try:
        port = int(info.netloc.split(':')[-1])
    except BaseException:
        if default_port is None:
            port = 443 if info.scheme == 'wss' else 80
        else:
            port = default_port

    return dict(port=port, path=path, host=host)
