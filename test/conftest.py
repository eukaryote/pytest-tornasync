import pytest

import tornado.web

from test import MainHandler

pytest_plugins = ["pytest_tornasync"]


@pytest.fixture
def app():
    return tornado.web.Application([(r"/", MainHandler)])
