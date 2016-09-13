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

MAX_WORKERS = 16

# PAPARAZZI_SERVER = "static-maps.dev.mapzen.com"
# PAPARAZZI_SERVER = "52.90.135.245"
PAPARAZZI_SERVER = "http://localhost:8080"
VALHALLA_SERVER = 'http://valhalla.mapzen.com'

SERVER = "localhost"
SERVER_PORT = 8010
ZOOM = 18
KINDLE_WIDTH = 758
KINDLE_HEIGHT = 1024
TMP_FOLDER = "tmp"

# Server GeoJSONs
class JSONHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        if os.path.isfile("tmp"+self.request.path):
            print "Opening " + "tmp"+self.request.path
            f = open("tmp"+self.request.path) 
            self.set_header('Content-type', 'application/json')
            self.write(f.read())
            f.close()            

#Server PDF's
class RouteHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def make_guide(self):
        print "SEARCHING ROUTE"
        # CHECK THIS
        print VALHALLA_SERVER+"/route?json="+self.get_arguments("json")[0]+"&api_key=valhalla-EzqiWWY"
        RST = requests.get(VALHALLA_SERVER+"/route?json="+self.get_arguments("json")[0]+"&api_key=valhalla-EzqiWWY")

        name = md5.new(RST.text).hexdigest()

        pdf_name = TMP_FOLDER+'/'+name+'.pdf'
        if os.path.isfile("tmp/"+name+".pdf"):
            with open(pdf_name, 'rb') as f:
                print "Serving cached PDF: " + pdf_name
                return f.read()


        print "Constructing PDF: "
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
        scene = getScene('http://' + SERVER + ':' + str(SERVER_PORT) + '/' + geojson_name);

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
            pdf.text(20, KINDLE_HEIGHT-4, instructions[step])
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
    print 'Starting httpd...'
    return tornado.web.Application([
        (r"\/[\w|\d]+\.json", JSONHandler),
        (r"/route.*", RouteHandler),
    ])

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        SERVER_PORT = int(argv[1])

    app = make_app()
    app.listen(SERVER_PORT)
    IOLoop.instance().start()
    # tornado.ioloop.IOLoop.current().start()
