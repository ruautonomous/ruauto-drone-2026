from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
from messages import MessageStream
from logger import logger, bcolors
# from mission import Mission # unused import currently

class Drone:

    home_position = {'lat': 0, 'long': 0, 'alt': 0}

    def __init__(self, parametersFile = None):
        self.home_position = {}
        self.message_stream = -1
        if(parametersFile):
            pass
        else:
            self.target_alt = 10# 10 meters
            self.threshhold = 2 # 2 meters

    def connect_drone(self,connection_string = 'tcp:127.0.0.1', port = 5763, baud = 57600):
        self.connection = mavutil.mavlink_connection(f'{connection_string}:{port}', baud)
        self.connection.wait_heartbeat()
        print(f"{bcolors.HEADER} Connected to {connection_string} on port {port} with system id {self.connection.target_system} and component id {self.connection.target_component} {bcolors.ENDC}")
        
    def set_message_stream(self, message_stream: MessageStream):
         self.message_stream = message_stream

    

    async def set_home_position(self):
        print('REQUESTING GPS')
        gps = await self.message_stream.request_message(common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT)
        
        
        self.home_position['lat'] = gps.lat
        self.home_position['long'] = gps.lon
        self.home_position['alt'] = gps.relative_alt
        print(self.home_position)
        print(f'GPS IS {gps}')
        # print(gps)
        
    async def get_position(self):
        current_pos = await self.message_stream.request_message(common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT)
        return [gps.lat, gps.lon, gps.relative_alt]
    

    async def start_processes(self, stream: asyncio.Queue, parametersFile = None):
        if parametersFile:
            pass
            
        await asyncio.gather(self.message_stream.message_stream(), logger(stream), self.set_home_position())


    async def send_command(self, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0):
        await self.message_stream.send_command(command=command, 
                                               param1=param1, param2=param2, param3=param3, param4=param4, param5=param5,param6=param6, param7=param7)
    
    def get_home_position(self):
        return self.home_position
    
    def get_connection(self):
        return self.connection

    def get_queue(self):
        return self.message_queue
    
    async def get_message_stream(self):
        if not self.message_stream == -1:
            return self.message_stream
        await asyncio.sleep(0.1)