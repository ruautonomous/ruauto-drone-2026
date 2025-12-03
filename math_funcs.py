
import math

def calculate3Ddist(x: list[3] = [0,0,0],y: list[3] = [0,0,0]):
    x1,y1,z1 = x
    x2,y2,z2 = y

    distance = math.sqrt(
        math.pow(x2-x1, 2) + math.pow(y2-y1,2) + math.pow(z2-z1,2)
    )
    return distance




