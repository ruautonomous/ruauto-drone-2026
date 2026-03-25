import asyncio 
from pymavlink import mavutil 
from pymavlink.dialects.v20 import common

from utils.drone import Drone


class Camera:
    def __init__(self, drone: Drone):
        self.drone = drone
        pass