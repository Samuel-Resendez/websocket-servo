#Author: Samuel Resendez

import tornado.ioloop
import tornado.web
import tornado.websocket

import json, math

from tornado.options import define, options, parse_command_line

define("port", default=5000, help="run on the given port", type=int)

clients= [] #All clients that are currently connected
curr_data_patterns = [0,0,0,0]




class IndexHandler(tornado.web.RequestHandler):


    def post(self):
        longitude = self.get_argument('longitude','No Data Received')
        latitude = self.get_argument('latitude', 'No Data Received')

        dat_dict = {"longitude":longitude,"latitude":latitude}
        for c in clients:
            c.write_message(json.dumps(dat_dict))

        self.finish()


    def get(self):

        self.render('index.html')


class dataPatternHandler(tornado.web.RequestHandler):


    def get(self):
        self.write("""
        <h2> POST endpoint for pattern handling </h2>
        <li> params: {'pattern_id':Int(0-N)}</li>
        <li> returns: 500 or 200 </li>
        <p> Things to know: <br> It will add if the dataset is not currently displayed <br>
        And it will remove it if it is. It is YOUR responsibility to keep track which datasets <br>
        are up and which ones aren't. </p>
        """)


    def post(self):
        pattern = self.get_argument('pattern_id','No Data Received')
        if pattern == 'No Data Received':
            self.write("Error: 500")
            self.finish()
        else:
            pattern = int(pattern)
            if pattern > 3:
                pattern = 3
            elif pattern < 0:
                pattern = 0
            if curr_data_patterns[pattern-1] == 0:
                curr_data_patterns[pattern-1] = 1
            else:
                curr_data_patterns[pattern-1] = 0

            dat_dict = {'bin':curr_data_patterns}
            for c in clients:
                c.write_message(json.dumps(dat_dict))


        self.write("Succes:: 200")
        self.finish()


class leapRotationHandler(tornado.web.RequestHandler):

    def post(self):
        zoomFac = self.get_argument('zoomFactor','No Data Received')
        if zoomFac == 'No Data Received':
            self.write("Error: 500")
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

class MapStyleHandler(tornado.web.RequestHandler):

    def post(self):
        map_style = self.get_argument("map_style","No Data Received")
        if map_style == "No Data Received":
            self.write("Error: 500")
            self.finish()
        else:
            map_style = int(map_style)
            if map_style < 0:
                map_style = 0
            elif map_style > 2:
                map_style = 2
            dat_dict = {"map_style":map_style}
            for c in clients:
                c.write_message(json.dumps(dat_dict))
        self.write("Success: 200")
        self.finish()


    def get(self):
        self.write("""
        <h1> POST endpoint for Map Style Setting
        <li>params: {map_style: Int(0-N)}</li>
        <li>returns: 500 on failure, 200 on success </li>
        """)
        self.finish()

class LeapWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):

        return True

    def open(self):
        print("Websocket Open")


    def on_message(self, message):
        for c in clients:
            c.write_message(message)

    def on_close(self):
        print("Websocket Closed")


def say_hi():
    for c in clients:
        c.write_message("hi")

class EchoWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in clients:
            clients.append(self)
        print("WebSocket opened on /websocket")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in clients:
            clients.remove(self)
        print("WebSocket closed: " + str(len(clients)))


if __name__ == '__main__':
    parse_command_line()

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/websocket', EchoWebSocket),
        (r'/Leap',leapRotationHandler),
        (r'/LeapPosition',LeapWebSocket),
        (r'/alexaPosition',alexaPositionDeltaHandler),
        (r'/setDataPattern',dataPatternHandler),
        (r'/setMapStyle',MapStyleHandler)
    ])

    app.listen(options.port)

    tornado.ioloop.PeriodicCallback(say_hi, 2000).start()
   
    tornado.ioloop.IOLoop.instance().start()
