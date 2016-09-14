#!/usr/bin/env python

import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor   # `pip install futures` for python2

from valhala import getShape, getStops, getInstructions
from tangram import getScene

from fpdf import FPDF
from PIL import Image

from StringIO import StringIO
import sys
import os

import geojson
import json
import md5
import requests
import socket

MAX_WORKERS = 16

PAPARAZZI_SERVER = "http://localhost:8080"
VALHALLA_SERVER = 'http://valhalla.mapzen.com'

SERVER = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
ZOOM = 18.5
KINDLE_WIDTH = 758
KINDLE_HEIGHT = 1024
TMP_FOLDER = "tmp"
WWW_FOLDER = "www"

# Server GeoJSONs
class WebServer(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        if self.request.path is '/':
            self.request.path = '/index.html'

        if os.path.isfile(WWW_FOLDER+self.request.path):
            file_name, file_ext = os.path.splitext(self.request.path)
           
            mime_header = 'text/html'
            if file_ext == '.css':
                mime_header = 'text/css'
            elif file_ext == '.yaml':
                mime_header = 'text/vnd.yaml'
            elif file_ext == '.js':
                mime_header = 'application/javascript'
            elif file_ext == '.svg':
                mime_header = 'image/svg+xml'

            # print 'Sending', file_name, file_ext, 'as', mime_header

            f = open(WWW_FOLDER+self.request.path)
            self.set_header('Content-type', mime_header)
            self.write(f.read())
            f.close()   

# Server GeoJSONs
class JSONHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        if os.path.isfile(TMP_FOLDER+self.request.path):
            print "Opening " + TMP_FOLDER+self.request.path
            f = open(TMP_FOLDER+self.request.path) 
            self.set_header('Content-type', 'application/json')
            self.write(f.read())
            f.close()            

#Server PDF's
class RouteHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def make_guide(self):
        # CHECK THIS
        print  "New ROUTE", VALHALLA_SERVER+"/route?json="+self.get_arguments("json")[0]+"&api_key="+self.get_arguments("api_key")[0]
        RST = requests.get(VALHALLA_SERVER+"/route?json="+self.get_arguments("json")[0]+"&api_key="+self.get_arguments("api_key")[0])

        name = md5.new(RST.text).hexdigest()

        pdf_name = TMP_FOLDER+'/'+name+'.pdf'
        if os.path.isfile("tmp/"+name+".pdf"):
            with open(pdf_name, 'rb') as f:
                print "Serving CACHED PDF: " + pdf_name
                return f.read()

        print "Constructing NEW PDF"

        # Make a GeoJSON file with valhala response
        geojson_name = name+'.json'
        JSON = json.loads(RST.text)
        shape = getShape(JSON['trip']['legs'][0])
        stops = getStops(JSON['trip']['legs'][0])
        instructions = getInstructions(JSON['trip']['legs'][0])
        feature_collection = geojson.FeatureCollection([geojson.Feature(geometry=geojson.LineString(shape)), geojson.Feature(geometry=geojson.MultiPoint(stops))])

        # Save it to serve it to paparazzi
        json_path = TMP_FOLDER+'/'+geojson_name
        file = open(json_path, 'w')
        file.write(geojson.dumps(feature_collection, sort_keys=True))
        file.close()

        # Emebed the link into a YAML scene file
        scene = getScene('http://' + SERVER + '/' + geojson_name);

        # Start a PDF
        pdf = FPDF(unit = 'pt', format = [KINDLE_WIDTH, KINDLE_HEIGHT])
        pdf.set_margins(0,0)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_fill_color(255,255,255)

        # Iterate through the instructions
        step = 0
        while step < len(stops):
            params = { 'width': KINDLE_WIDTH, 'height': KINDLE_HEIGHT-40 }
            params['zoom'] = ZOOM
            params['lon'] = stops[step][0]
            params['lat'] = stops[step][1]

            # Get a static map per instruction
            response = requests.post(PAPARAZZI_SERVER, params=params, data=scene);
            img = Image.open(StringIO(response.content))
            img = img.convert('L')
            img_path = TMP_FOLDER+'/'+name+'-'+str(step)+'.png'
            img.save(img_path)

            # Add a new page with the instruction at the bottom
            pdf.add_page()
            pdf.image(img_path,0,0)
            # pdf.rect(0, KINDLE_HEIGHT-20, KINDLE_WIDTH, 20, 'F')
            pdf.text(10, KINDLE_HEIGHT-14, instructions[step])
            step = step + 1

            # Clean image
            os.remove(img_path)

        # Clean GeoJSON
        os.remove(json_path)

        # Cach response 
        pdf.output(pdf_name, "F")
        return pdf.output(dest="S")

    @tornado.gen.coroutine
    def get(self):
        self.set_header('Content-type', 'application/pdf');
        res = yield self.make_guide()
        self.write(res)

def make_app():
    print 'Pointing Paparazzi server at:', PAPARAZZI_SERVER
    print 'Starting HTTP Server at:', 'http://'+SERVER
    return tornado.web.Application([
        (r"\/[\w|\d]+\.json", JSONHandler),
        (r"/route.*", RouteHandler),
        (r"/.*", WebServer),
    ])

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        PAPARAZZI_SERVER = argv[1]

    app = make_app()
    app.listen(80)
    IOLoop.instance().start()
