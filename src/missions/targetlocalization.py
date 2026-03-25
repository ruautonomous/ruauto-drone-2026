import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone, DroneProperties
from utils.takeoff import *
from utils.speed import change_speed
import utils.mode as mode
from utils.armdisarm import *
from utils.reposition import reposition_drone_deg



class TargetLocalization:
    def __init__(self, drone: Drone, initFile: str = None):
        self.drone = drone
        pass


    async def begin_dummy_mission(self):
        await arm_drone(self.drone)
        await mode.set_mode(drone=self.drone, mode=mode.GUIDED)
        await takeoff(drone=self.drone, target_alt=10)
        await reposition_drone_deg(self.drone, [-35.3618419,149.1651785,10])
        await change_speed(self.drone, 15)

