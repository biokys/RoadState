#!/usr/bin/python
import os
import generate_tiles

helper_file = '/home/biokys/PREPARED/helper.dat'

#bbox = (13.15, 48.61, 17.17, 50.87)
minZoom = 8
maxZoom = 14
outputDir = "/var/www/tiles2/"
#outputDir = "tiles3/"


with open(helper_file, 'rw+') as file:
    for line in file:
        data = line.split(' ')
        bbox = (float(data[1]), float(data[0]), float(data[3]), float(data[2]))
        print('Computing tiles for data: ' + str(bbox))
        generate_tiles.render_tiles(bbox, outputDir, minZoom, maxZoom)
    file.truncate(0)

