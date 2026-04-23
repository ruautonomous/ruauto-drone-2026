import asyncio 
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.takeoff import *
from utils.armdisarm import *
from utils.reposition import *
import utils.mode as mode

class PackageDrop:

    def __init__(self, drone: Drone):
        self.drone = drone
        pass

    async def upload_mission(self):
        pass
