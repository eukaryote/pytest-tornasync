from pytest_tornasync.plugin import *

from test import MainHandler


@pytest.fixture
def app():
    return tornado.web.Application([(r"/", MainHandler)])
