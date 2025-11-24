from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio

class Takeoff:


    def __init__(self, drone: mavutil.mavtcp):
        self.drone = drone
        pass

    
from drone import Drone

class Fence:

    def __init__(self, drone: Drone):
        self.drone = drone
        pass

        async def bs():
            await self.drone.message_stream.send_command(common.MAV_CMD_DO_FENCE_ENABLE,param1=1, param2=common.FENCE_TYPE_POLYGON)

