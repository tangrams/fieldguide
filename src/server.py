#!/usr/bin/env python

import tornado.ioloop
import tornado.web

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

class JSONHandler(tornado.web.RequestHandler):
    def get(self):
        if os.path.isfile("tmp"+self.request.path):
            print "Opening " + "tmp"+self.request.path
            f = open("tmp"+self.request.path) 
            self.set_header('Content-type', 'application/json')
            self.write(f.read())
            f.close()

class RouteHandler(tornado.web.RequestHandler):
    def get(self):
        print "SEARCHING ROUTE"
        # CHECK THIS
        print VALHALLA_SERVER+"/route?json="+self.get_arguments("json")[0]+"&api_key=valhalla-EzqiWWY"
        RST = requests.get(VALHALLA_SERVER+"/route?json="+self.get_arguments("json")[0]+"&api_key=valhalla-EzqiWWY")

        name = md5.new(RST.text).hexdigest()
        geojson_name = name+'.json'
        JSON = json.loads(RST.text)
        
        shape = getShape(JSON['trip']['legs'][0])
        stops = getStops(JSON['trip']['legs'][0])
        instructions = getInstructions(JSON['trip']['legs'][0])

        feature_collection = geojson.FeatureCollection([geojson.Feature(geometry=geojson.LineString(shape)), geojson.Feature(geometry=geojson.MultiPoint(stops))])
        # route = StringIO(geojson.dumps(feature_collection, sort_keys=True))
        json_path = TMP_FOLDER+'/'+geojson_name
        file = open(json_path, 'w')
        file.write(geojson.dumps(feature_collection, sort_keys=True))
        file.close()

        scene = getScene('http://' + SERVER + ':' + str(SERVER_PORT) + '/' + geojson_name);

        pdf = FPDF(unit = 'pt', format = [KINDLE_WIDTH, KINDLE_HEIGHT])
        pdf.set_margins(0,0)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_fill_color(255,255,255)

        step = 0
        while step < len(stops):
            params = { 'width': KINDLE_WIDTH, 'height': KINDLE_HEIGHT }
            params['zoom'] = ZOOM
            params['lon'] = stops[step][0]
            params['lat'] = stops[step][1]

            response = requests.post(PAPARAZZI_SERVER, params=params, data=scene);

            img = Image.open(StringIO(response.content))
            img = img.convert('L')
            img_path = TMP_FOLDER+'/'+name+'-'+str(step)+'.png'
            img.save(img_path)

            pdf.add_page()
            pdf.image(img_path,0,0)
            pdf.rect(0, KINDLE_HEIGHT-20, KINDLE_WIDTH, 20, 'F')
            pdf.text(10, KINDLE_HEIGHT-4, instructions[step])
            step = step + 1

            os.remove(img_path)

        os.remove(json_path)

        print "RETURNING field guide"
        
        fieldguide = pdf.output("S");
        pdf.output(TMP_FOLDER+'/'+name+'.pdf', "F")

        self.set_header('Content-type', 'application/pdf')
        self.set_header('Content-length', len(fieldguide))
        self.write(pdf.output("S"))
        self.flush()

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
    tornado.ioloop.IOLoop.current().start()
