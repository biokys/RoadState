
number_list = []
def put_number(number):
    number_list.append(number)

def get_biggest_numbers(count):
    number_list.sort()
    return number_list[(len(number_list) - count):]

def get_average(count_num):
    'Metoda vraci prumer poslednich n prvku v seznamu'
    nlist = get_biggest_numbers(count_num)
    count = len(nlist)
    sum = 0
    for i in range(count):
        sum += nlist[i]
    return sum/count
    
def clear_list():
    del number_list[1:]
    return

minLat = 10000
minLng = 10000
maxLat = -10000
maxLng = -10000

def put_coord(lat, lng):
    global minLat
    global minLng
    global maxLat
    global maxLng
    if lat < minLat:
        minLat = lat
    if lat > maxLat:
        maxLat = lat
    if lng < minLng:
        minLng = lng
    if lng > maxLng:
        maxLng = lng
    return

def get_minmax_rectangle():
    return [minLat, minLng, maxLat, maxLng]

def reset_minmax_rectangle():
    minLat = 10000
    minLng = 10000
    maxLat = -10000
    maxLng = -10000
    return

#for i in range(-20,20):
#    put_coord(i*3, i*4)
    
#print(get_minmax_rectangle())


