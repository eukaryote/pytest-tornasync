================
pytest-tornasync
================

.. image:: https://travis-ci.org/eukaryote/pytest-tornasync.svg?branch=master
    :target: https://travis-ci.org/eukaryote/pytest-tornasync

A simple pytest plugin that provides some helpful fixtures for testing
Tornado (version 5.0 or newer)  apps and easy handling of plain
(undecoratored) native coroutine tests (Python 3.5+).

Why another Tornado pytest plugin when the excellent ``pytest-tornado`` already
exists? The main reason is that I didn't want to have to decorate every test
coroutine with ``@pytest.mark.gen_test``. This plugin doesn't have anything
like ``gen_test``. Defining a test with ``async def`` and a name that
begins with ``test_`` is all that is required.


Installation
------------

Install using pip, which must be run with Python 3.5+:

.. code-block:: sh

    pip install pytest-tornasync


Usage
-----

Define an ``app`` fixture:

.. code-block:: python

    import pytest


    @pytest.fixture
    def app():
        import yourapp
        return yourapp.make_app()  # a tornado.web.Application


Create tests as native coroutines using Python 3.5+ ``async def``:

.. code-block:: python

    async def test_app(http_server_client):
        resp = await http_server_client.fetch('/')
        assert resp.code == 200
        # ...


Fixtures
--------

When the plugin is installed, then ``pytest --fixtures`` will show
the fixtures that are available:

http_server_port
    Port used by `http_server`.
http_server
    Start a tornado HTTP server that listens on all available interfaces.

    You must create an `app` fixture, which returns
    the `tornado.web.Application` to be tested.

    Raises:
    FixtureLookupError: tornado application fixture not found
http_server_client
    Create an asynchronous HTTP client that can fetch from `http_server`.
http_client
    Create an asynchronous HTTP client that can fetch from anywhere.
io_loop
    Create a new `tornado.ioloop.IOLoop` for each test case.



Examples
--------

.. code-block:: python

    import time

    import tornado.web
    import tornado.gen

    import pytest


    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Hello, world!")


    @pytest.fixture
    def app():
        return tornado.web.Application([(r"/", MainHandler)])


    async def test_http_server_client(http_server_client):
        # http_server_client fetches from the `app` fixture and takes path
        resp = await http_server_client.fetch('/')
        assert resp.code == 200
        assert resp.body == b"Hello, world!"


    async def test_http_client(http_client):
        # http_client fetches from anywhere and takes full URL
        resp = await http_client.fetch('http://httpbin.org/status/204')
        assert resp.code == 204


    async def example_coroutine(period):
        await tornado.gen.sleep(period)


    async def test_example():
        # no fixtures needed
        period = 1.0
        start = time.time()
        await example_coroutine(period)
        elapsed = time.time() - start
        assert elapsed >= period
