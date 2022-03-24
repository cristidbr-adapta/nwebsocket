# test_utils.py

import pytest

from nwebsocket.utils import uriparse

def test_uri_parsing(  ):
    # regular WS
    result = uriparse( 'ws://locatest1/test1' )  
    assert {'port': 80, 'path': '/test1', 'host': 'locatest1'} == result

    # secure WS
    result = uriparse( 'wss://locatest2/test2' )  
    assert {'port': 443, 'path': '/test2', 'host': 'locatest2'} == result

    # path check
    result = uriparse( 'ws://locatest3' )  
    assert {'port': 80, 'path': '', 'host': 'locatest3'} == result

    # port check
    result = uriparse( 'wss://10.0.0.4:8001/test4' )  
    assert {'port': 8001, 'path': '/test4', 'host': '10.0.0.4'} == result

    # port check
    result = uriparse( 'ws://10.0.0.5/test5' )  
    assert {'port': 80, 'path': '/test5', 'host': '10.0.0.5'} == result

    # default_port check
    result = uriparse( 'wss://locatest6:8006/test6', default_port=-8006 )  
    assert {'port': 8006, 'path': '/test6', 'host': 'locatest6'} == result

    # noscheme check
    result = uriparse( '//locatest7/test7', default_port=8007 )  
    assert {'port': 8007, 'path': '/test7', 'host': 'locatest7'} == result

