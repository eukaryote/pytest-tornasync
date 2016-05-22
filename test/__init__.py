import tornado.web

MESSAGE = 'Hello, world!'
PAUSE_TIME = 0.05


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(MESSAGE)
