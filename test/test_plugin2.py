import asyncio

import pytest


@pytest.fixture
def io_loop():
    yield asyncio.SelectorEventLoop()


@pytest.mark.xfail(type=TypeError)
async def test_bad_io_loop_fixture(io_loop):
    assert False  # won't be run
