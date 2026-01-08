from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
from drone import Drone
import utils.file_reader as file_reader
from modes import Modes
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