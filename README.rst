nwebsocket 
##########
    
.. image:: https://badge.fury.io/py/nwebsocket.svg?
    :target: https://badge.fury.io/py/nwebsocket.svg
    :alt: Python Package Index

.. image:: https://img.shields.io/pypi/pyversions/nwebsocket?    
    :target: https://img.shields.io/pypi/pyversions/nwebsocket   
    :alt: PyPI - Python Version

.. image:: https://codecov.io/gh/cristidbr-adapta/nwebsocket/branch/main/graph/badge.svg?token=0ZXGWE8SQZ
    :target: https://codecov.io/gh/cristidbr-adapta/nwebsocket
    :alt: Code Coverage

.. image:: https://github.com/cristidbr-adapta/nwebsocket/actions/workflows/CI.yml/badge.svg
    :target: https://github.com/cristidbr-adapta/nwebsocket/actions/workflows/CI.yml
    :alt: Continuous Integration

Simple and easy to use syncronous WebSocket client, no async.

Usable with `Jupyter Notebook`_. 

.. _Jupyter Notebook: https://jupyter.org/ 

Installation
============

Install using pip
::

    pip install nwebsocket 

Python version
--------------

Python 3.7+ is required.

Usage
=====

Raw API 
-------

A simple example without classes

.. code:: python

    # example_minimal.py
    from nwebsocket import WebSocket 

    wscn = WebSocket( "wss://ws.postman-echo.com/raw" )

    wscn.onmessage = lambda m: print( m )
    wscn.onopen = lambda: print( "Opened connection" )
    wscn.onclose = lambda: print( "Closed connection" )
    wscn.onerror = lambda: print( "Connection errored out" )

    print( wscn.readyState )

    wscn.send( 'text' )

Class protocol 
--------------

Example of extending the WebSocket class. 



Motivation
==========

There are many asynchronous Python WebSocket client packages out there, and 
almost of them require your code to use the async syntax. This is unfortunate,
since it will lead to a **run_until_complete** call eventually, which will 
block the main thread from performing other operations in parrallel.

Inspiration 
===========

This package was inspired by the ultra-simple WebSocket API in the JavaScript 
language, which it replicates one-to-one.

https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/url


Guideline
=========

Since the callback-style API is quite unusual when it comes to pythonicity,
your task will be to:

- define **onmessage**, **onopen**, **onclose** and **onerror**
- handle reconnection/s
- implement the TX/RX specification for working with the endpoint
- isolate the callback pattern from the rest of your code


Take a chat service as an example, there are operations which are following 
the traditional request/response pattern such as posting messages, and there 
are other messages which are received without issuing a request (chat posting 
by other users).

These latter messages must be handled by your code as soon as they are received. 
Class instances can help with that, by storing the received information (chat 
posts). Keep your callbacks short, fast and serializable.


Limitations
===========

This library is not suitable for high throughput, as the queue mechanism in Python 
is notoriously slow due to serialization.


License (MIT)
=============

Copyright (C) 2022 `Adapta Robotics`_ | `MATT Robot`_ 

.. _MATT Robot: https://mattrobot.ai
.. _Adapta Robotics: https://adaptarobotics.com  
