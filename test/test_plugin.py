import time

import tornado.gen
import tornado.ioloop
import tornado.web

import pytest

from test import MESSAGE, PAUSE_TIME


class ExpectedError(RuntimeError):

    """
    A dedicated error type for raising from tests to verify a fixture was run.
    """


@pytest.fixture
def mynumber():
    return 42


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(MESSAGE)


def _pause_coro(period):
    return tornado.gen.sleep(period)


async def pause():
    await _pause_coro(PAUSE_TIME)


def test_plain_function():
    # non-coroutine test function without fixtures
    assert True


def test_plain_function_with_fixture(mynumber):
    # non-coroutine test function that uses a fixture
    assert mynumber == 42


async def nontest_coroutine(io_loop):
    # Non-test coroutine function that shouldn't be run
    assert False


def nontest_function(io_loop):
    # Non-test function that shouldn't be run
    assert False


async def test_pause(io_loop):
    start = time.time()
    await pause()
    elapsed = time.time() - start
    assert elapsed >= PAUSE_TIME


async def test_http_client_fetch(http_client, http_server, http_server_port):
    url = "http://localhost:%s/" % http_server_port[1]
    resp = await http_client.fetch(url)
    assert resp.code == 200
    assert resp.body.decode("utf8") == MESSAGE


async def test_http_server_client_fetch(http_server_client):
    resp = await http_server_client.fetch("/")
    assert resp.code == 200
    assert resp.body.decode("utf8") == MESSAGE


@pytest.mark.xfail(raises=ExpectedError)
def test_expected_noncoroutine_fail():
    raise ExpectedError()


@pytest.mark.xfail(raises=ExpectedError)
async def test_expected_coroutine_fail_no_ioloop():
    """A coroutine test without an io_loop param."""
    raise ExpectedError()


@pytest.mark.xfail(raises=ExpectedError)
async def test_expected_coroutine_fail_io_loop(io_loop):
    """A coroutine test with an io_loop param."""
    raise ExpectedError()


@pytest.mark.xfail(strict=True, raises=tornado.ioloop.TimeoutError)
@pytest.mark.timeout(seconds=0.1)
async def test_timeout(io_loop):
    await _pause_coro(0.15)
