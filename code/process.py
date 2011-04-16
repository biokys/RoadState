#!/usr/bin/python
import zipfile, glob, os, math
from time import time
import helper

# CONFIG
#input_dir = '../PACKAGES'
input_dir = '/mnt/hgfs/storage'
output_dir = '/home/biokys/PREPARED'



output_file_row_count = 50

speedthreshold = 2
accuracythreshold = 10

# PROGRAM 


def procdata(data, filename):
    _name = filename.split('_')
    timestamp = _name[0]
    speed = float(_name[3])
    accuracy = float(_name[4])
    if speed < speedthreshold:
        _speed = False
    else:
        _speed = True
    
    if accuracy < accuracythreshold:
        _accuracy = True
    else:
        _accuracy = False
    
    lines = (data.split())
    sum = 0;
    if (_accuracy == True and _speed == True):
        for _line in lines: 
            __line = _line.decode("utf-8").split(',')
            result1 = recalc(__line[0], __line[1], __line[2])
            helper.put_number(result1)
        r1 = helper.get_average(5) * 100
        helper.clear_list()
        s = timestamp + ' ' + _name[1] + ' ' + _name[2] + ' ' + str(r1)
        #helper.put_coord(float(_name[1]), float(_name[2]))
        add_to_file(s + '\n')
    
    return

def listZip(name):
    file = zipfile.ZipFile(name, "r")
    for name in file.namelist():
        data = file.read(name)
        procdata(data, name)
    return

def recalc_difficult(accX, accY, accZ, oX, oY):
    accX = math.fabs(float(accX))
    accY = math.fabs(float(accY))
    accZ = math.fabs(float(accZ)) - 9.81
    oX = float(oX)
    oY = float(oY)
    #if oX<90:
    #rx =  oX / 90
    # rx = math.sin((3.14*oX)/180)
    #else:
    # rx = 2 - (oX / 90)
    rx = math.sin((3.14 * oX) / 180)
    ry = math.sin((3.14 * oY) / 180)
    #ry =  oY / 90
    temp_g_x = ry * 9.81
    temp_g_y = rx * 9.81
    az = (1 - ry - rx) * accZ 
    ax = ry * (accX - temp_g_x)
    ay = rx * (accY - temp_g_y)
    result = math.sqrt(math.pow(ax, 2) + math.pow(ay, 2) + math.pow(az, 2))
    return result

def recalc(accX, accY, accZ):
    vector_magnitude = math.sqrt(math.pow(float(accX), 2) + math.pow(float(accY), 2) + math.pow(float(accZ), 2))
    return (vector_magnitude/9.81)


def add_to_file(data):
    out_f.write(data);
    return


# main routine
file_name = str(int(time()*100))
# file for storing calculated datas
out_f = open(output_dir + '/' + file_name + '.PROC' , 'w')
count = 0
for infile in glob.glob(os.path.join(input_dir, '*.zip')):
    #helper.reset_minmax_rectangle()
    count = count + 1
    print(infile)
    listZip(infile)
    #add_to_help_file(helper.get_minmax_rectangle())
    os.rename(infile, infile + '.UNZIPPED')
out_f.close()
#helper_f.close()
if count == 0:
    print('no file(s) found...')
    os.remove(output_dir + '/' + file_name + '.PROC')
else:
    print(str(count) + ' file(s) processed...')    
    os.rename(output_dir + '/' + file_name + '.PROC', output_dir + '/' + file_name + '.DONE')





# list file information
#for info in file.infolist():
#    print(info.filename, info.date_time, info.file_size)
