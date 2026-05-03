
import math

def calculate3Ddist(x: list[3] = [0,0,0],y: list[3] = [0,0,0]):
    x1,y1,z1 = x
    x2,y2,z2 = y


    distance = math.sqrt(
        math.pow(x2-x1, 2) + math.pow(y2-y1,2) + math.pow(z2-z1,2)
    )
    return distance


# haversine is used for calculating distances on a spherical planet DONT USE A REGULAR 3D DISTANCE FORMULA THATS ONLY FOR FLAT SURFACES

import math

def haversine_distance(x: list[3] = [0,0,0],y: list[3] = [0,0,0]):
    '''takes two coordinates (lat,long in degrees NOT SCALED BY 1e7 and altitude in METERS) and finds the distance between then. Return value in METERS'''
    lat1, lon1, alt1 = x
    lat2, lon2, alt2 = y
    R = 6371.0
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Horizontal distance in meters
    horizontal_dist = R * c * 1000
    
    # Vertical distance (difference in altitude)
    vertical_dist = alt2 - alt1
    
    # Resultant 3D distance using Pythagorean theorem
    return math.sqrt(horizontal_dist**2 + vertical_dist**2)
