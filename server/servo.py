#Author: Samuel Resendez

import tornado.ioloop
import tornado.web
import tornado.websocket
import json, math

from tornado.options import define, options, parse_command_line

define("port", default=5000, help="run on the given port", type=int)

clients= []

class IndexHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def post(self):
        longitude = self.get_argument('longitude','No Data Received')
        latitude = self.get_argument('latitude', 'No Data Received')

        dat_dict = {"longitude":longitude,"latitude":latitude}
        for c in clients:
            c.write_message(json.dumps(dat_dict))

        self.finish()

    @tornado.web.asynchronous
    def get(self):

        self.render('index.html')


class leapRotationHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def post(self):
        zoomFac = self.get_argument('zoomFactor','No Data Received')
        if zoomFac == 'No Data Received':
            self.write("Post Failed")
            self.finish()
        zoomFac = float(zoomFac)
        isPostiive = True
        if zoomFac < 0:
            isPostiive = False

        zoomFac = 3 / (1 + 3*math.exp(-.01*abs(zoomFac)))
        if isPostiive:
            zoomFac = - zoomFac
        else:
            zoomFac = zoomFac
        print(zoomFac)
        dat_dict = {'zoomFactor':zoomFac}
        for c in clients:
            c.write_message(json.dumps(dat_dict))

        self.write("200")
        self.finish()

class alexaPositionDeltaHandler(tornado.web.RequestHandler):

    def post(self):
        position = self.get_argument('zoom_delta','No Data Received')
        if position == 'No Data Received':
            self.write("Error Code: 500")
            self.finish()
        else:
            position = int(position)
            dat_dict = {'zoomFactor':position}
            for c in clients:
                c.write_message(json.dumps(dat_dict))
            self.write("Success: 200")
            self.finish()

class leapPositionHandler(tornado.web.RequestHandler):
    def post(self):
        position = self.get_argument('position','No Data Received')
        if position == 'No Data Received':
            self.write(500)
            self.finish()
        else:
            position = int((7/225)*int(position) + (85/9))
            if position > 25:
                position = 25

            dat_dict = {'zoomValue':position}
            for c in clients:
                c.write_message(json.dumps(dat_dict))
            self.write("200")
            self.finish()


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
        if self in clients:
            clients.remove(self)
        print("WebSocket closed")

if __name__ == '__main__':
    parse_command_line()

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/websocket', EchoWebSocket),
        (r'/Leap',leapRotationHandler),
        (r'/LeapPosition',leapPositionHandler),
        (r'/alexPosition',alexaPositionDeltaHandler),
    ])
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
