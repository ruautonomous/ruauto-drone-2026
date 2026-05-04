import asyncio 
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.takeoff import *
from utils.armdisarm import *
from utils.reposition import *
import utils.mode as mode

class PackageRecovery:
    
    def __init__(self, drone: Drone, initFile = None):
        self.drone = drone
        self.file = initFile

    async def upload_mission(self, rtl:bool = True):
        pass
    