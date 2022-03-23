"""
nwebsocket/utils
~~~~~~~~~~~~~~~~

URL Parsing utilities.
"""

from urllib.parse import urlparse

def uriparse( uri, default_port = 8080 ):
    info = urlparse( uri )
    host = info.netloc.split( ':' )[ 0 ]
    path = info.path 

    try: 
        port = int( info.netloc.split( ':' )[ -1 ] )
    except:
        port = default_port
    
    return dict( port = port, path = path, host = host )
