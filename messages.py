from pymavlink import mavutil
from pymavlink.dialects.v20 import common 
import asyncio
from logger import log_custom, log_system, bcolors
from utils.file_reader import read_file

class MessageStream:
    stream = asyncio.Queue()
    important_msg = dict()
    important = []

    def __init__(self, drone: mavutil.mavtcp):
        self.drone = drone
        self.initialize_important_messages()

        pass

    def initialize_important_messages(self):
        if not self.drone is None:
            self.important = read_file('info_files/important_messages.txt')
            print(f'initialized all important messages :) --> {self.important}')
        

    async def request_message(self, message_id: int, drone: mavutil.mavtcp = None):
        if drone is None:
            drone = self.drone

        await self.send_command(command= common.MAV_CMD_REQUEST_MESSAGE, param1= message_id)

        target_message = common.mavlink_map.get(message_id).msgname
        return await self.wait_for_message(target_message)

            
    async def send_command(self, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0):
        
        self.drone.mav.command_long_send(self.drone.target_system, self.drone.target_component, command, 0, 
                                         param1,param2,param3,param4,param5,param6,param7)
        
        ack =  await self.wait_for_message(f'COMMAND_ACK.{command}')
        
        log_custom(f'recieved command ack code: {command}')
        if(ack.result != 0):
            log_system(msg = "PASSING INTO RESULT HANDLER...STANDBY", msgname="ACK_HANDLER")
            await self.result_handler(ack, command, param1, param2, param3, param4,param5,param6,param7)
        return ack # no harm in return the command_ack
        
    async def result_handler(self, ack, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0):
        match ack.result:
            case 1: # MAV_RESULT_TEMPORARILY_REJECTED
                log_system(msg = "MAV RESULT TEMP REJECTED. RETRYING COMMAND IN 1 SECOND", msgname="ACK_HANDLER (RETRYING)")
                await asyncio.sleep(1)
                self.send_command(command, 
                           param1, param2, param3, param4, param5, param6, param7)
            case 2: # MAV_RESULT_DENIED
                log_system(msgname="ACK_HANDLER (ERROR)", color=bcolors.FAIL, msg="MAV RESULT FAILED. ONE OR MORE PARAMETERS INVALID")
            case 3: # MAV_RESULT_UNSUPPORTED
                log_system(msg="COMMAND UNSUPPORTED", msgname="ACK_HANDLER (UNSUPPORTED)")
            case 4: #MAV_RESULT_FAILED
                log_system(msgname="ACK_HANDLER (FAILED)", msg="COMMAND FAILED TO EXECUTE. UNEXPECTED PROBLEM OCCURED")
        pass

    # 11/26/25 -> Updated this class to be able to wait for multiple messages (useful for mission_request & mission_request_int)
    async def wait_for_message(self, *msgs): 
        while True:
            for msg in msgs:
                if(self.important_msg.__contains__(msg)):
                    ack = self.important_msg.pop(msg)
                    # print(f'Recieved {msg}') # REMOVE THIS LATER
                    return ack
            # print(f'Waiting for {msg}') # REMOVE THIS LATER
            await asyncio.sleep(0.2)
        
        

    
    async def message_stream(self):
        while True:
            msg = self.drone.recv_match(blocking=False)
            if msg:
                await self.handle_message(msg)
            await asyncio.sleep(0.1)

    async def handle_message(self, msg):
        await self.stream.put(msg)
        if self.important.__contains__(msg.msgname):
            self.important_msg[f'{msg.msgname}'] = msg
            # print(f'Added {msg.msgname} to important message dict')

        elif msg.msgname == 'COMMAND_ACK':
            self.important_msg[f'{msg.msgname}.{msg.command}'] = msg

        elif msg.msgname == 'MISSION_ACK':
            self.important_msg[f'{msg.msgname}.{msg.mission_type}'] = msg
        
        
