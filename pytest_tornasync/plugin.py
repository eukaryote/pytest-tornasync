import inspect

import tornado.ioloop
import tornado.testing
import tornado.simple_httpclient

import pytest

try:
    iscoroutinefunction = inspect.iscoroutinefunction
except AttributeError:
    def iscoroutinefunction(obj):
        return False


def get_test_timeout(pyfuncitem):
    timeout = pyfuncitem.config.option.async_test_timeout
    marker = pyfuncitem.get_marker('timeout')
    if marker:
        timeout = marker.kwargs.get('seconds', timeout)
    return timeout


def pytest_addoption(parser):
    parser.addoption('--async-test-timeout', type=float,
                     help=('timeout in seconds before failing the test '
                           '(default is no timeout)'))
    parser.addoption('--app-fixture', default='app',
                     help=('fixture name returning a tornado application '
                           '(default is "app")'))


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name) and iscoroutinefunction(obj):
        return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    try:
        event_loop = pyfuncitem.funcargs['io_loop']
    except KeyError:
        return True

    if not isinstance(event_loop, tornado.ioloop.IOLoop):
        raise TypeError("unsupported event loop type: %s" % type(event_loop))

    funcargs = pyfuncitem.funcargs
    testargs = {arg: funcargs[arg]
                for arg in pyfuncitem._fixtureinfo.argnames}

    event_loop.run_sync(lambda: pyfuncitem.obj(**testargs),
                        timeout=get_test_timeout(pyfuncitem))
    return True


def _loop_create(klass):
    loop = klass()
    loop.make_current()
    return loop


def _loop_destroy(loop):
    loop.clear_current()
    if not type(loop).initialized() or loop is not type(loop).instance():
        loop.close(all_fds=True)


@pytest.yield_fixture
def io_loop_tornado():
    """
    Create a new `tornado.ioloop.IOLoop` for each test case.
    """
    io_loop = _loop_create(tornado.ioloop.IOLoop)
    yield io_loop
    _loop_destroy(io_loop)


@pytest.yield_fixture
def io_loop_asyncio():
    """
    Create a new `tornado.platform.asyncio.AsyncIOLoop` for each test case.
    """
    io_loop = _loop_create(tornado.platform.asyncio.AsyncIOLoop)
    yield io_loop
    _loop_destroy(io_loop)


@pytest.fixture
def io_loop(io_loop_tornado):
    """
    Alias for `io_loop_tornado`, by default.

    You may define an `io_loop` that uses the `io_loop_asyncio` fixture to
    use an asyncio-backed Tornado event loop.
    """
    return io_loop_tornado


@pytest.fixture
def http_server_port():
    """
    Port used by `http_server`.
    """
    return tornado.testing.bind_unused_port()


@pytest.yield_fixture
def http_server(request, io_loop, http_server_port):
    """Start a tornado HTTP server that listens on all available interfaces.

    You must create an `app` fixture, which returns
    the `tornado.web.Application` to be tested.

    Raises:
        FixtureLookupError: tornado application fixture not found
    """
    http_app = request.getfuncargvalue(request.config.option.app_fixture)
    server = tornado.httpserver.HTTPServer(http_app, io_loop=io_loop)
    server.add_socket(http_server_port[0])

    yield server

    server.stop()

    if hasattr(server, 'close_all_connections'):
        io_loop.run_sync(server.close_all_connections,
                         timeout=request.config.option.async_test_timeout)


class AsyncHTTPServerClient(tornado.simple_httpclient.SimpleAsyncHTTPClient):

    def initialize(self, io_loop, *, http_server=None):
        super().initialize(io_loop)
        self._http_server = http_server

    def fetch(self, path, **kwargs):
        """
        Fetch `path` from test server, passing `kwargs` to the `fetch`
        of the underlying `tornado.simple_httpclient.SimpleAsyncHTTPClient`.
        """
        return super().fetch(self.get_url(path), **kwargs)

    def get_protocol(self):
        return 'http'

    def get_http_port(self):
        for sock in self._http_server._sockets.values():
            return sock.getsockname()[1]

    def get_url(self, path):
        return '%s://localhost:%s%s' % (self.get_protocol(),
                                        self.get_http_port(), path)


@pytest.yield_fixture
def http_server_client(http_server):
    """
    Create an asynchronous HTTP client that can fetch from `http_server`.
    """
    client = AsyncHTTPServerClient(http_server.io_loop,
                                   http_server=http_server)
    yield client
    client.close()


@pytest.yield_fixture
def http_client(http_server):
    """
    Create an asynchronous HTTP client that can fetch from anywhere.
    """
    client = tornado.httpclient.AsyncHTTPClient(http_server.io_loop)
    yield client
    client.close()
