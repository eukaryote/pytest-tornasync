import pytest

import tornado.web

from test import MainHandler


@pytest.fixture
def app():
    return tornado.web.Application([(r"/", MainHandler)])
