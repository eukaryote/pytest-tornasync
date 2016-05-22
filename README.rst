================
pytest-tornasync
================

.. image:: https://travis-ci.org/eukaryote/pytest-tornasync.svg?branch=master
    :target: https://travis-ci.org/eukaryote/pytest-tornasync


A simple pytest plugin that provides some helpful fixtures for testing
Tornado apps and easy handling of plain (undecoratored) native coroutine tests (Python 3.5+).


Usage
-----

When the plugin is installed, then ``py.test --fixtures`` will show
the fixtures that are available.

The minimal setup is to define an ``app`` fixture that provides a
Tornado app.

Test cases must be native coroutines defined using `async def` if they
should be run using the event loop provided by the `io_loop` fixture, but
the `io_loop` and other async helper fixtures do not need to be used.

Some examples::

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


    async def pause(period):
        await tornado.gen.sleep(period)


    async def test_pause():
        # no decorator or fixture required for this to run in event loop
        period = 1.0
        start = time.time()
        await pause(period)
        elapsed = time.time() - start
        assert elapsed >= period


    async def test_http_server_client(http_server_client):
        # http_server_client fetches from the `app` fixture and takes path
        resp = await http_server_client.fetch('/')
        assert resp.code == 200
        assert resp.body == b"Hello, world!"


    async def test_http_client(http_client):
        # http_client fetches from anywhere and takes full URL
        resp = await http_client.fetch('http://httpbin.org/status/204')
        assert resp.code == 204

