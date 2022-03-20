nwebsocket 
##########

Python package for simple and easy to use WebSocket clients without async. 

Inspiration 
===========

This package was inspired by the ultra-simple WebSocket API in the JavaScript 
language which it replicates. 

https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/url

Motivation
==========

There are many asynchronous Python WebSocket client packages out there, and 
almost of them require your code to use the async syntax. This one does not, 
so it's easier to use from within a Jupyter Notebook. All of the async code 
is executed within a separate thread.

Guideline
=========

Since the callback-style API is quite unusual when it comes to pythonicity,
your task will be to:

- define **onmessage**, **onopen**, **onclose** and **onerror**
- handle reconnection/s
- implement the TX/RX specification for working with the endpoint
- isolate the callback pattern from the rest of your code


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
