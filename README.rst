nwebsocket 
##########

Python package for simple and easy to use WebSockets.

Inspiration 
===========

This package was inspired by the ultra-simple WebSocket API in the JavaScript 
language which it replicates. 

https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/url

Installation
============

Install using pip
::

    pip install nwebsocket 

Python version
--------------

Python 3.6+ is required.

Usage
=====

A simple minimal API interface can be created using the following example.

.. code:: python

    # minimal.py
    from nwebsocket import WebSocket 

    wscn = new WebSocket( "ws://localhost:8001" )

    wscn.onmessage = lambda m: print( m )
    wscn.onopen = lambda: print( "Opened connection" )
    wscn.onclose = lambda: print( "Closed connection" )
    wscn.onerror = lambda: print( "Connection errored out" )

    print( wscn.readyState )

License (MIT)
=============

Copyright (C) 2022 `Adapta Robotics`_ .

.. _Adapta Robotics: https://adaptarobotics.com 
