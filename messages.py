from pymavlink import mavutil
from pymavlink.dialects.v20 import common 
import asyncio

from logger import log_message

# Purpose: To have functions that will

class MessageStream:
    def __init__(self, drone: mavutil.mavtcp):
        self.drone = drone
        pass

    async def request_message(self, message_id: int, drone: mavutil.mavtcp = None):
        if drone is None:
            drone = self.drone
        
        
        drone.mav.command_long_send(drone.target_system, drone.target_component, common.MAV_CMD_REQUEST_MESSAGE, 1, 
                                    message_id, 0, 0,0,0,0,0)
        common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT

        while True:
            msg = drone.recv_match(type=f'{common.mavlink_map.get(message_id).msgname}', blocking = False)
            await asyncio.sleep(0.1)
            if msg: 
                return msg
            
            

    async def message_getter(self, message_id: int, drone: mavutil.mavctp):
        if drone is None:
            drone = self.drone

        msg = drone.recv_match(type=f'{common.mavlink_map.get(message_id).msgname}', blocking=False)
        await asyncio.sleep(1)
        if(msg):
            return msg
