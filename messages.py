from pymavlink import mavutil
from pymavlink.dialects.v20 import common 
import asyncio


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

        await self.send_command(command= common.MAV_CMD_REQUEST_MESSAGE, param1= message_id)

        target_message = common.mavlink_map.get(message_id).msgname
        await self.wait_for_message(target_message)

        # while True:
        #     if(self.important_msg.__contains__(target_message)):
        #         print(f'Removing {target_message} from important_msg list')
        #         return self.important_msg.pop(target_message)
        #     await asyncio.sleep(0.2)
            
    async def send_command(self, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0):
        
        self.drone.mav.command_long_send(self.drone.target_system, self.drone.target_component, command, 0, 
                                         param2,param3,param4,param1,param5,param6,param7)
        
        await self.wait_for_message(msg=f'COMMAND_ACK.{command}')
        print('recieved command ack')
        return
        # while True:
            
        #     if(self.important_msg.__contains__(f'COMMAND_ACK.{command}')):
        #         ack = self.important_msg.pop(f'COMMAND_ACK.{command}')
        #         print('YAY WE GOT THE COMMAND ACK ') 
        #         # if ack mav_result == accepted, then true, else return fail
        #     await asyncio.sleep(0.2)
        
    async def wait_for_message(self, msg):
        while True:
            if(self.important_msg.__contains__(msg)):
                ack = self.important_msg.pop(msg)
                return ack
            await asyncio.sleep(0.2)

    
    async def message_stream(self):
        while True:
            msg = self.drone.recv_match(blocking=False)
            if msg:
                await self.handle_message(msg)
            await asyncio.sleep(0.1)

    async def handle_message(self, msg):

        if self.important.__contains__(msg.msgname):
            self.important_msg[f'{msg.msgname}'] = msg
            print(f'Added {msg.msgname} to important message dict')

        elif msg.msgname == 'COMMAND_ACK':
            self.important_msg[f'{msg.msgname}.{msg.command}'] = msg

        elif msg.msgname == 'MISSION_ACK':
            self.important_msg[f'{msg.msgname}.{msg.mission_type}'] = msg
        
        await self.stream.put(msg)
