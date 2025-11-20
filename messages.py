from pymavlink import mavutil
from pymavlink.dialects.v20 import common 
import asyncio

from logger import log_message, logger

# Purpose: To have functions that will

class MessageStream:
    stream = asyncio.Queue()
    important_msg = dict()
    important = []

    def __init__(self, drone: mavutil.mavtcp):
        self.drone = drone
        self.initialize_important_messages()
        
        pass

    def initialize_important_messages(self):
        # read a list with all messages we need to watch for (GLOBAL_POSITION_INT, MISSION_REQUEST, etc) and add it to self.important
        # DO later if this strategy for messages works

        if not self.drone is None:
            print('initialized all important messages :)')
            self.important = ['GLOBAL_POSITION_INT', 'MISSION_REQUEST', 'MISSION_REQUEST_INT']
        pass

    async def request_message(self, message_id: int, drone: mavutil.mavtcp = None):
        if drone is None:
            drone = self.drone
        
        
        drone.mav.command_long_send(drone.target_system, drone.target_component, common.MAV_CMD_REQUEST_MESSAGE, 1, 
                                    message_id, 0, 0,0,0,0,0)
        common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT

        while True:
            target_message = common.mavlink_map.get(message_id).msgname
            if(self.important_msg.__contains__(target_message)):
                print(f'Removing {target_message} from important_msg list')
                return self.important_msg.pop(target_message)
            await asyncio.sleep(0.2)
            
    async def send_command(self, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0):
        
        self.drone.mav.command_long_send(self.drone.target_system, self.drone.target_component, command, 0, 
                                         param2,param3,param4,param1,param5,param6,param7)
        
        while True:
            if(self.important_msg.__contains__(f'COMMAND_ACK.{command}')):
                ack = self.important_msg.pop(f'COMMAND_ACK.{command}')
                    
        pass
            
    async def message_stream(self):
        while True:
            msg = self.drone.recv_match(blocking=False)
            if msg:
                # log_message(msg) # Logs said message
                if self.important.__contains__(msg.msgname):
                    self.important_msg[f'{msg.msgname}'] = msg
                    print(f'Added {msg.msgname} to important message dict')
                elif msg.msgname == 'COMMAND_ACK':
                    self.important_msg[f'{msg.msgname}.{msg.command}'] = msg
                elif msg.msgname == 'MISSION_ACK':
                    self.important_msg[f'{msg.msgname}.{msg.mission_type}'] = msg
                else:
                    await self.stream.put(msg)
            await asyncio.sleep(0.1)