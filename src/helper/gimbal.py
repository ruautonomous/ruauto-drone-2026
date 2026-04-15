import asyncio
from pymavlink.dialects.v20 import common
from utils.drone import Drone

class GimbalManager:
    def __init__(self, drone: Drone):
        self.drone = drone
        pass

    async def configure_gimbal(self):
        await self.drone.send_command(common.MAV_CMD_DO_MOUNT_CONFIGURE, 1,1,1,1,1,1)

    async def reposition_gimbal(self):
        self.drone = None

'''USE MAV_CMD_DO_MOUNT_CONTROL to control the gimbal orientation'''