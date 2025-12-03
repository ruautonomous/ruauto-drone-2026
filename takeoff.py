from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio

class Takeoff:


    def __init__(self, drone: mavutil.mavtcp):
        self.drone = drone
        pass

