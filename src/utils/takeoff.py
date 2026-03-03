import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.armdisarm import arm_drone, disarm_drone
import utils.mode as mode
from utils.logger import log_system, log_success

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
    await wait_for_altitude_increase(drone, target_alt, msgname="Takeoff Handler")

async def return_to_launch(drone: Drone):
    await mode.set_mode(drone=drone, mode=mode.RTL)
    home_pos = await drone.get_home_position_deg()
    await wait_for_altitude_decrease(drone, home_pos['alt'], msgname="RTL Handler")
    await mode.set_mode(drone=drone, mode=mode.STABILIZE)
    await disarm_drone(drone)


async def wait_for_altitude_increase(drone: Drone, target_alt, msgname="Increasing Altitude"):
    while True:
        current_pos = await drone.get_position_deg()
        if current_pos['alt'] > (1-drone.threshholdZ)*target_alt:
            log_success(msgname=msgname, msg="Climb to target altitude complete!")
            return
        log_system(msg=f"Current Altitude: {current_pos['alt']} | Target Altitude: {target_alt}", msgname=msgname)
        await asyncio.sleep(1)

async def wait_for_altitude_decrease(drone: Drone, target_alt, msgname="Decreasing Altitude"):
    while True:
        current_pos = await drone.get_position_deg()
        if current_pos['alt'] < (1+drone.threshholdZ)*target_alt:
            log_success(msgname=msgname, msg="Decline to target altitude complete!")
            return
        log_system(msg=f"Current Altitude: {current_pos['alt']} | Target Altitude: {target_alt}", msgname=msgname)
        await asyncio.sleep(1)