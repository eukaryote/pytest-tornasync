"""
Test that needs to be in a separate module to define an altenate `io_loop`.
"""

from asyncio import SelectorEventLoop

import pytest


@pytest.fixture
def io_loop():
    """
    A non `tornado.ioloop.IOLoop` for testing purposes.
    """
    yield SelectorEventLoop()


@pytest.mark.xfail(raises=TypeError)
def test_bad_io_loop(io_loop):
    pass
