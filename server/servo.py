#Author: Samuel Resendez

import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

clients= []

class IndexHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def post(self):
        long = self.get_argument('longitude','No Data Received')
        lat = self.get_argument('latitude', 'No Data Received')

        print(int(long), int(lat))

        for c in clients:
            c.write_message(str((long, lat)))

        self.finish()

    @tornado.web.asynchronous
    def get(self):

        self.render('index.html')


class EchoWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in clients:
            clients.append(self)

        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):

        print("WebSocket closed")

if __name__ == '__main__':
    parse_command_line()

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/websocket', EchoWebSocket),
    ])
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
