import asyncio
from pymavlink.dialects.v20 import common
from pymavlink import mavutil

from utils.drone import Drone
from utils.logger import log_system
from utils.takeoff import takeoff, return_to_launch
import utils.mode as mode
from utils.armdisarm import *

'''This is for missions for testing the autonomous capabilities of the drone'''


async def takeoff_land(drone: Drone, hold_time: int = 30, alt: int = 5):
    '''Mission 10 - Tests takeoff and land'''
    log_system(msgname="Simple Takeoff Land Mission Activated",msg=f"Test mission started. Takeoff to {alt} meters, hold for {hold_time} seconds and land")
    await takeoff(drone=drone, target_alt=alt)
    # await mode.set_mode(drone, mode.ALTHOLD) # Oddly, switching to ALTHOLD causes copter to return to launch
    while hold_time > 0:
        if hold_time % 5 == 0 or hold_time < 6:
            log_system(msgname="Simple Takeoff Land Mission HOLD",msg=f"Holding current altitude for {hold_time} seconds")
        await asyncio.sleep(1)
        hold_time -= 1
    
    await return_to_launch(drone=drone)
    pass