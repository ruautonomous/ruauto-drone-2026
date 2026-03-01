import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone

async def reposition_drone_deg(drone: Drone, coordinate: list = None):
    await drone.message_stream_exists()
    await drone.send_command(command=common.MAV_CMD_DO_REPOSITION, 
                             param1=drone.groundspeed, 
                             param2=common.MAV_DO_REPOSITION_FLAGS_CHANGE_MODE, 
                             param5=list[0],
                             param6=list[1],
                             param7=list[2])
    pass