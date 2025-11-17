from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio

class Mission:
    def __init__(self, drone:mavutil.mavtcp):
        self.drone = drone
        pass

    async def mission_setup(self):
        pass

    async def upload_mission(self):
        pass