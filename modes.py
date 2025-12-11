from pymavlink import mavutil
from pymavlink.dialects.v20 import common
from drone import Drone
from messages import MessageStream
import math_funcs, asyncio
from logger import log_custom
class Modes:

    # add more modes from FLTMODE1 if this system works
    # https://ardupilot.org/copter/docs/parameters.html#fltmode1
    mode_map = {'stabilize': 0, 'auto': 3, 'guided': 4, 'loiter': 5, 'rtl': 6}

    def __init__(self, drone: Drone):
        self.drone  = drone
        self.message_stream: MessageStream  = drone.get_message_stream
        pass

    async def arm_drone(self):
        # await self.check_stream()
        ack = await self.message_stream.send_command(common.MAV_CMD_COMPONENT_ARM_DISARM, param1=1, param2=0)

    async def disarm_drone(self):
        ack = await self.message_stream.send_command(common.MAV_CMD_COMPONENT_ARM_DISARM, param1=0, param2=0)
    
    async def set_mode(self, mode: str):
        mode_ack = await self.drone.send_command(common.MAV_CMD_DO_SET_MODE, 1, self.mode_map[mode.lower()])
        pass


    async def rtl(self):
        log_custom(f'Return to launch initiated', True)
        await self.set_mode('rtl')

        if(len(self.drone.get_home_position()) < 1):
            await asyncio.sleep(1)

        homeX, homeY, homeZ = self.drone.get_home_position().values()
        current_pos = [0,0,0]
        while True:
            current_pos = await self.drone.get_position()

            if(math_funcs.calculate3Ddist(current_pos, [homeX, homeY, homeZ]) < self.drone.threshhold):
                break

            await asyncio.sleep(2)
        await self.set_mode('stabilize')
        log_custom(f'Returned to launch successfully at >\nLat: {current_pos[0]}\nLong: {current_pos[1]}\nAlt: {current_pos[2]}', True)
