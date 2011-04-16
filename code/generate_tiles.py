#!/usr/bin/python
from math import pi, cos, sin, log, exp, atan
from subprocess import call
import sys, os, random
import Image, ImageDraw
import MySQLdb

#bbox = (13.15, 48.61, 17.17, 50.87)
#minZoom = 6
#maxZoom = 12
#outputDir = "/var/www/tiles/"
#outputDir = "tiles2/"

DEG_TO_RAD = pi / 180
RAD_TO_DEG = 180 / pi

# Default number of rendering threads to spawn, should be roughly equal to number of CPU cores available
NUM_THREADS = 4

IMG_WIDTH = 256.0
IMG_HEIGHT = 256.0


def minmax (a, b, c):
    a = max(a, b)
    a = min(a, c)
    return a

class GoogleProjection:
    def __init__(self, levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0, levels):
            e = c / 2;
            self.Bc.append(c / 360.0)
            self.Cc.append(c / (2 * pi))
            self.zc.append((e, e))
            self.Ac.append(c)
            c *= 2
                
    def fromLLtoPixel(self, ll, zoom):
        d = self.zc[zoom]
        e = round(d[0] + ll[0] * self.Bc[zoom])
        f = minmax(sin(DEG_TO_RAD * ll[1]), -0.9999, 0.9999)
        g = round(d[1] + 0.5 * log((1 + f) / (1 - f)) * -self.Cc[zoom])
        return (e, g)
     
    def fromPixelToLL(self, px, zoom):
        e = self.zc[zoom]
        f = (px[0] - e[0]) / self.Bc[zoom]
        g = (px[1] - e[1]) / -self.Cc[zoom]
        h = RAD_TO_DEG * (2 * atan(exp(g)) - 0.5 * pi)
        return (f, h)


def get_data_from_db(x,y,x1,y1):
    c = db.cursor()
    c.execute('SELECT avg(average) FROM clusters WHERE latitude>' + str(y1) + ' AND latitude<' + str(y) + ' AND longitude>' + str(x) + ' AND longitude<' + str(x1))
    avg = c.fetchone()
    #if avg[0] != None:
        #print(avg[0])
    #print(str(y) + ' ' + str(x) + ' ' + str(y1) + ' ' + str(x1) + ' ' + str(avg[0]))
    return avg[0]


# vrati matici 256x256 obsahujici jiz hotove pixely
def get_data_matrix(x, y, x1, y1):
    matrix = []
    d = db.cursor()
    d.execute('SELECT avg(average) FROM clusters WHERE latitude>' + str(y1) + ' AND latitude<' + str(y) + ' AND longitude>' + str(x) + ' AND longitude<' + str(x1))
    avg = d.fetchone()
    #print(str(x) + ' ' + str(y) + ' ' + str(x1) + ' ' + str(y1))
    if avg[0] != None:
        delta_x = x1 - x
        delta_y = y1 - y
        step_x = delta_x / (IMG_WIDTH/4)
        step_y = delta_y / (IMG_HEIGHT/4)
        for i in range(int(IMG_WIDTH/4)):
            m = []
            for j in range(int(IMG_HEIGHT/4)):
                px = x + (i*step_x)
                py = y + (j*step_y)
                px1 = x + ((i+1)*step_x)
                py1 = y + ((j+1)*step_y)
                k = get_data_from_db(px, py, px1, py1)
    	        if k == None:
    	            k=0
                m.append(int(k))
            matrix.append(m)
                #print(str(px) + ' ' + str(py) + ' ' + str(px1) + ' ' + str(py1))
    else:
        for i in range(int(IMG_WIDTH/4)):
            m = []
            for j in range(int(IMG_HEIGHT/4)):
                m.append(0)
            matrix.append(m)
        print('no data, skipping...')
    return matrix

_red = 0
_green = 0
_blue = 0
def imagedrawing(filename, x, y, x1, y1, z):
    p = 0 
    mat = get_data_matrix(x, y, x1, y1)
    image = Image.new("RGBA",(IMG_WIDTH,IMG_HEIGHT), (255,255,255,0)) 
    draw = ImageDraw.Draw(image)
    x = 0
    for i in mat:
        y = 0
        for j in i:
            pos = ((x-1)*4+4,(y-1)*4+4),((x+2)*4+4,(y+2)*4+4)
            if j == 0:
                draw.rectangle(pos,fill=(0,0,0,0))
            else:
                if j < 98: 
                    j = 98
                if j > 120:
                    j = 120
                i2 = 120
                i1 = 98
                interval = i2 - i1
                c = interval/100.0
                p = (j-i1)/c
                draw.rectangle(pos, fill=((2.55*int(p)),2.55*(100-int(p)),0))
            y+=1
        x+=1
    image.save(open(filename, "wb"), "PNG")
    return


def render_tiles(bbox, tile_dir, minZoom=1, maxZoom=18):
    if not os.path.isdir(tile_dir):
        os.mkdir(tile_dir)
    gprj = GoogleProjection(maxZoom + 1) 
    ll0 = (bbox[0], bbox[3])
    ll1 = (bbox[2], bbox[1])

    for z in range(minZoom, maxZoom + 1):
        px0 = gprj.fromLLtoPixel(ll0, z)
        px1 = gprj.fromLLtoPixel(ll1, z)

        # check if we have directories in place
        zoom = "%s" % z
        if not os.path.isdir(tile_dir + zoom):
            os.mkdir(tile_dir + zoom)
        for x in range(int(px0[0] / IMG_WIDTH), int(px1[0] / IMG_HEIGHT) + 1):
            # Validate x co-ordinate
            if (x < 0) or (x >= 2 ** z):
                continue
            # check if we have directories in place
            str_x = "%s" % x
            if not os.path.isdir(tile_dir + zoom + '/' + str_x):
                os.mkdir(tile_dir + zoom + '/' + str_x)
            for y in range(int(px0[1] / IMG_WIDTH), int(px1[1] / IMG_HEIGHT) + 1):
                # Validate x co-ordinate
                if (y < 0) or (y >= 2 ** z):
                    continue
                str_y = "%s" % y
                tile_uri = tile_dir + zoom + '/' + str_x + '/' + str_y + '.png'
                # Submit tile to be rendered into the queue
                [xx,yy] = gprj.fromPixelToLL([ x * IMG_WIDTH,y * IMG_HEIGHT], z)
                [xx1,yy1] = gprj.fromPixelToLL([ (x+1) * IMG_WIDTH,(y+1) * IMG_HEIGHT], z)
                print(tile_uri)
                imagedrawing(tile_uri, xx, yy, xx1, yy1, z)
    return

db = MySQLdb.connect(user="root", passwd="12345678", db="roadstate")

#render_tiles(bbox, outputDir, minZoom, maxZoom)


    
