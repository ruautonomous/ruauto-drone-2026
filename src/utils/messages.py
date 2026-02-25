import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common
from utils.logger import log_custom, log_message, log_system, bcolors
import io.file_reader as reader 

class MessageStream:

    
    def __init__(self, connection: mavutil.mavfile):
        self.important_messages = None
        self.stored_messages: dict[str, asyncio.Future] = {}
        self.connection = connection
        logger.log_message(msg="Initializing Message Stream")
        self.stream = asyncio.Queue()
        
        asyncio.create_task(self.message_stream())
        
        pass

    def initialize_important_messages(self):
        if not self.connection is None:
            self.important_messages = reader.read_file('info_files/important_messages.txt')
            print(f'initialized all important messages :) --> {self.important_messages}')

    async def message_stream(self):
        while True:
            msg = self.connection.recv_match(blocking=False)
            if msg:
                await self.handle_message(msg)
            await asyncio.sleep(0.01)

    async def request_message(self, message_id: int, drone: mavutil.mavtcp = None):
        if drone is None:
            drone = self.connection

        await self.send_command(command= common.MAV_CMD_REQUEST_MESSAGE, param1= message_id)

        target_message = common.mavlink_map.get(message_id).msgname
        return await self.wait_for_message(target_message)

            
    async def send_command(self, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0):
        
        self.drone.mav.command_long_send(self.drone.target_system, self.drone.target_component, command, 0, 
                                         param1,param2,param3,param4,param5,param6,param7)
        
        # ack =  await self.wait_for_message(f'COMMAND_ACK.{command}')
        try:
            ack = await asyncio.wait_for(self.wait_for_message(f'COMMAND_ACK.{command}'), timeout=5)
            log_custom(f'recieved command ack code: {command}')
        except TimeoutError:
            log_system(color=bcolors.FAIL, msg=f"FAILED TO RECIEVE COMMAND_ACK ({command})")
            return

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
    async def wait_for_message(self, *msgs, secondary = '1'): 
        while True:
            for msg in msgs:
                
                future = asyncio.get_running_loop().create_future()

                if self.important_messages.__contains__(msg.msgname):
                    # print(f'Added {msg.msgname} to important message dict')
                    if msg.msgname == 'COMMAND_ACK':
                        self.stored_messages[f'{msg.msgname}.{secondary}'] = future
                    elif msg.msgname == 'MISSION_ACK':
                        self.stored_messages[f'{msg.msgname}.{secondary}'] = future
                    else:
                        self.stored_messages[f'{msg.msgname}'] = future

                await future
                return future.result()
                # if(self.stored_messages.__contains__(msg)):
                #     ack = self.stored_messages.pop(msg)
                #     # print(f'Recieved {msg}') # REMOVE THIS LATER
                #     return ack
            # print(f'Waiting for {msg}') # REMOVE THIS LATER
            # await asyncio.sleep(0.2)

    async def handle_message(self, msg):
        await self.stream.put(msg)
        if self.important_messages.__contains__(msg.msgname):
            if msg.msgname == 'COMMAND_ACK':
                self.stored_messages[f'{msg.msgname}.{msg.command}'].set_result(msg)
            elif msg.msgname == 'MISSION_ACK':
                self.stored_messages[f'{msg.msgname}.{msg.mission_type}'].set_result(msg)
            else:
                self.stored_messages[f'{msg.msgname}'].set_result(msg)
                common.mavlink_map
        
        
    