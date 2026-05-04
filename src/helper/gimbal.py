import asyncio
from pymavlink.dialects.v20 import common
from utils.drone import Drone


async def reposition_gimbal(drone: Drone, roll:float = 0, pitch:float = 0, yaw:float = 0):
    await drone.send_command(command=common.MAV_CMD_DO_MOUNT_CONTROL, param1=pitch, param2=roll,param3=yaw, param7=2)
    pass     

'''USE MAV_CMD_DO_MOUNT_CONTROL to control the gimbal orientation'''