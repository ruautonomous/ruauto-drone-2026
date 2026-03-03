import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.armdisarm import arm_drone
import utils.mode as mode


async def takeoff(drone: Drone, target_alt = None, lat = None, long = None):
    if not target_alt:
        target_alt = drone.target_alt
    if not (lat and long):
        pos = await drone.get_position_deg()
        lat = pos["lat"]
        long = pos["long"]
        
    await arm_drone(drone=drone)
    await mode.set_mode(drone=drone, mode=mode.GUIDED)
    await drone.send_command(command=common.MAV_CMD_NAV_TAKEOFF, param5 = lat, param6 = long, param7 = target_alt)