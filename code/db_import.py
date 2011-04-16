#!/usr/bin/python
import geohelper
import sys
import glob
import os
import MySQLdb
import logging
import helper

LOG_FILENAME = '/tmp/import_db.log'

source_file_dir = '/home/biokys/PREPARED'
output_dir = '/home/biokys/PREPARED'


point_vector = ()
global_list = []
cluster_list = []

clustering_threshold = 5

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

def insert_point(vector):
    timestamp = vector[0]
    lat = vector[1]
    lng = vector[2]
    factor = vector[3]
    point_vector = (int(timestamp), float(lat), float(lng), float(factor))
    global_list.append(point_vector)
    return
    
def print_list(l):
    for i in l:
        print(i)
    return
        
# vrati podmnozinu zaznamu, ktere se nachazeji ve ctverci lat1, lng1, lat2, lng2       
def get_list(lat1, lng1, lat2, lng2):
    local_list = []
    for i in cluster_list:
        if lat1 < i[1] < lat2 and lng1 < i[2] < lng2:
            local_list.append(i)     
    return local_list

def show_progress_bar(percent, length):
    status_bar='['
    for l in range(length):
        if l <= (percent/(100/length)):
            status_bar+='='
        else:
            status_bar+='-'
    status_bar+=']' 
    return status_bar 
        
counter = 0        
num_calculate = 0
ratio = clustering_threshold * 0.00005
loop_counter = 0

def proc(infile):
    file = open(infile, 'r')    
    while 1:
        line = file.readline()                  # nactu jeden radek
        if not line: break                      # pokud uz zadny neni, pak konec
        dataline = line.split()                 # rozdelim radek na pole
        v = tuple(dataline)                     # prevedu na tuple
        insert_point(v)                         # vlozim do seznamu
    file.close()                         
    return

def insert_point_db(v, clusterID):
    t = str(v[0])
    factor = str(v[3])
    c = db.cursor()
    c.execute("INSERT INTO datas (quality_factor, timestamp, ref_clusters) VALUES(" + factor + "," + t + "," + str(clusterID) + ")")
    helper.put_coord(v[1], v[2])
    return

def insert_cluster_db(v):
	lat = str(v[1])
	lng = str(v[2])
	c = db.cursor()
	c.execute("INSERT INTO clusters (latitude, longitude) VALUES(" + lat + "," + lng + ")")
	c.execute("SELECT id FROM clusters where latitude=" + lat + " AND longitude=" + lng)
	row = c.fetchone()

	return row[0]

def get_clusters_db(lat1, lng1, lat2, lng2):
	#print(str(lat1) + ' ' + str(lng1) + ' ' + str(lat2) + ' ' + str(lng2))
	c = db.cursor()
	c.execute("SELECT id, latitude, longitude FROM clusters WHERE latitude>" + str(lat1) + " AND latitude<" + str(lat2) + " AND longitude>" + str(lng1) + " AND longitude<" + str(lng2))
	result = c.fetchall()
	return result

def get_clusters_count():
	c = db.cursor()
	c.execute("SELECT COUNT(*) FROM clusters")
	row = c.fetchone()
	return row[0]

def add_to_help_file(data):
    helper_f.write(str(data[0]) + ' ' + str(data[1]) + ' ' + str(data[2]) + ' ' + str(data[3]) + '\n')
    return

isFiles = False

for infile in glob.glob(os.path.join(source_file_dir, '*.DONE')):
    print('reading file: ' + infile)
    logging.debug('reading file: ' + infile)
    isFiles = True
    proc(infile)
    
print('connecting to db...')
db = MySQLdb.connect(user="root", passwd="12345678", db="roadstate")
input_data_count = len(global_list)
print("num of points prepared to procces: " +  str(input_data_count))
logging.debug('point to process: ' + str(input_data_count))
print('processing...')    

clusterID = 0
print("raw data count: " + str(len(global_list)))
logging.debug('raw data count: ' + str(len(global_list)))
while len(global_list) > 0:
	in_cluster = False
	percent = int(loop_counter*100/input_data_count)
	status_bar = show_progress_bar(percent, 20)
	#sys.stdout.write('\r[' + str(loop_counter) + '/' + str(input_data_count) + ']\t' + status_bar)
	#sys.stdout.flush()
	loop_counter+=1
	v = global_list.pop()
	#print('clusters in db: ' + str(get_clusters_count()))
	if get_clusters_count() == 0:
		id = insert_cluster_db(v)
		insert_point_db(v, id)
		continue
	sub_list = get_clusters_db(v[1] - ratio, v[2] - ratio, v[1] + ratio, v[2] + ratio)
	for i in sub_list: 
		num_calculate+=1
		if geohelper.distance_in_meter(float(v[1]), float(v[2]), float(i[1]), float(i[2])) < clustering_threshold:
			in_cluster = True
			counter+=1
			insert_point_db(v, i[0])
			#print(sub_list)
			break
	if in_cluster == False:
		#cluster_list.append(v)
		id = insert_cluster_db(v)
		insert_point_db(v, id)
    
print('\n')    
logging.debug('proc finished')
for infile in glob.glob(os.path.join(source_file_dir, '*.DONE')):
    print('renaming file: ' + infile)
    os.rename(infile, infile + '.IMPORTED')
logging.debug('renaming finished')

if isFiles:
    # file for storing minmax rectanles for optimized rendering
    helper_f = open(output_dir + '/helper.dat', 'a') 
    add_to_help_file(helper.get_minmax_rectangle())

print('\n')
print('num of distance measurement calls: ' +  str(num_calculate))
print('num of found clusters: ' + str(len(cluster_list)))
logging.debug('measurement calls count: ' + str(num_calculate))
logging.debug('clusters found: ' + str(num_calculate))



