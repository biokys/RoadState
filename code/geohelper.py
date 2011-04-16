import math


eq_rad     = 6378.137 #eq radius in km
polar_rad  = 6356.752 #polar radius in km

def mercator_coords(geo_pt, center):
    '''
    Projects the given coordinates using Mercator projection
    with respect to `center`.
    '''

    x = geo_pt[0: , :1] - center[0]
    y = arctanh(math.sin(geo_pt[0 : , 1:]*(math.pi/360)))
    
    return hstack((x,y))


   
def distance_in_meter(lat1, lon1, lat2, lon2):
   '''
   Given a set of geo coordinates (in degrees) it will return the distance in km
   '''

   #convert to radians
   lon1 = lon1*2*math.pi/360
   lat1 = lat1*2*math.pi/360
   lon2 = lon2*2*math.pi/360
   lat2 = lat2*2*math.pi/360

   R = earth_radius((lat1+lat2)/2) #m

   #haversine formula - angles in radians
   deltaLon = abs(lon1-lon2)
   deltaLat = abs(lat1-lat2)

   dOverR = haver_sin(deltaLat) + math.cos(lat1)*math.cos(lat2)*haver_sin(deltaLon)

   return R * arc_haver_sin(dOverR)

def earth_radius(lat):
   '''
   Given a latitude in radias returns earth radius in metres
   '''

   top = (eq_rad**2 * math.cos(lat))**2 + (polar_rad**2 * math.sin(lat))**2
   bottom = (eq_rad * math.cos(lat))**2 + (polar_rad * math.sin(lat))**2
   
   return math.sqrt(top/bottom) * 1000

def haver_sin(x):
   return math.sin(x/2) ** 2

def arc_haver_sin(x):
   return 2*math.asin(math.sqrt(x))
   
   
def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * eq_rad * 1000