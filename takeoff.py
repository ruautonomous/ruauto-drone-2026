from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio

class Takeoff:


    def __init__(self, drone: mavutil.mavtcp):
        self.drone = drone
        pass



important = ['a','b']

a = 'a'
# print(important.__contains__(a))
# print(len(a))
# a = ['a','b']

# print(len(a))
a = ['a','c']
for msg in a:
    print(important.__contains__(msg))