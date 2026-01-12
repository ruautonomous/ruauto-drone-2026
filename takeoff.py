from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
from drone import Drone
import utils.file_reader as file_reader
from logger import log_system
from modes import Modes
import math
class Takeoff:


    def __init__(self, drone: Drone):
        self.drone = drone
        self.modes = Modes(drone)
        pass


    async def takeoff_from_current_pos(self, altitude = -1):
        if altitude == -1:
            altitude = self.drone.target_alt

        current_pos = await self.drone.get_position_deg()
        await self.modes.arm_drone()
        await self.modes.set_mode('guided')
        await self.drone.send_command(common.MAV_CMD_NAV_TAKEOFF, param5=current_pos[0], param6=current_pos[1], param7=altitude)
        await self.drone.send_command(command=common.MAV_CMD_DO_CHANGE_SPEED, param1=common.SPEED_TYPE_CLIMB_SPEED, param2=self.drone.climbspeed, param3=-1)

        await self.wait_to_reach_altitude(altitude=altitude)
        log_system(f'Drone takeoff complete to target altitude', msgname='TAKEOFF')

    async def wait_for_landing(self):
        await self.wait_to_reach_altitude(altitude=0)
        log_system(msg="Drone has landed successfully (hopefully)", msgname="RETURN TO LAUNCH")  

    async def wait_to_reach_altitude(self, altitude):
        while True:
            current_pos = await self.drone.get_position()
            if(abs(current_pos[2] - altitude) < self.drone.threshholdZ):
                break
            else:
                log_system(msg=f'Current Altitude is: {current_pos[2]}', msgname="CURRENT ALTITUDE")
                await asyncio.sleep(1)

    async def reset_drone(self): # used to change drone back to stabilize mode and disarm it
        await self.modes.set_mode('stabilize')
        await self.modes.disarm_drone()

# config = {}
# with open('info_files/config.txt') as f:
#     while True:
#         read = f.readline()
#         if(read == ''):
#             break
#         read = read.removesuffix('\n').split('=')
#         config[read[0]] = read[1]
#         print(f'{read}')
#     print(config)