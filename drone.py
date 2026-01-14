from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
from messages import MessageStream
from logger import logger, bcolors, log_system
from utils.file_reader import read_config_file

class Drone:

    home_position = {'lat': 0, 'long': 0, 'alt': 0}

    def __init__(self, parametersFile = None):
        self.home_position = {}
        self.message_stream = -1
        if(parametersFile):
            params = read_config_file(parametersFile)
            self.target_alt = int(params['altitude'])
            self.threshhold = float(params['threshhold'])
            self.threshholdZ = float(params['threshholdZ'])
            self.climbspeed = int(params['climbspeed'])
            self.airspeed = int(params['airspeed'])
        else:
            self.target_alt = 10 # 10 meters default
            self.threshhold = 2 # 2 meters default
            self.threshholdZ = 1 # 1 meter default
            self.climbspeed = -2
            self.airspeed = -2

        log_system(msg=f'Drone Parameters: \n    target_alt: {self.target_alt}\n    threshhold: {self.threshhold}')

        #TO DO - Remove the port parameter, itll come specified in the config file
    def connect_drone(self,connection_string = 'tcp:127.0.0.1', port = 5763, baud = 57600):
        self.connection = mavutil.mavlink_connection(f'{connection_string}:{port}', baud)
        self.connection.wait_heartbeat()
        print(f"{bcolors.HEADER} -- Connected to {connection_string} on port {port} with system id {self.connection.target_system} and component id {self.connection.target_component} --{bcolors.ENDC}")
        
    def set_message_stream(self, message_stream: MessageStream):
         self.message_stream = message_stream


    async def set_home_position(self):
        await asyncio.sleep(0.5)
        print('REQUESTING GPS')
        gps = await self.message_stream.request_message(common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT)
        
        
        self.home_position['lat'] = gps.lat
        self.home_position['long'] = gps.lon
        self.home_position['alt'] = gps.relative_alt
        print(self.home_position)
        print(f'GPS IS {gps}')
        # print(gps)
        
    async def get_position(self) -> list[int]:
        gps = await self.message_stream.request_message(common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT)
        return [gps.lat, gps.lon, gps.relative_alt/1000]
    
    async def get_position_deg(self):
        gps = await self.get_position()
        gps[0] = (float)(gps[0]/1e7)
        gps[1] = (float)(gps[1]/1e7)
        return gps
    
    async def start_processes(self, stream: asyncio.Queue):
        # self.modes = Modes(self)
        await asyncio.gather(self.message_stream.message_stream(), self.set_home_position(), logger(stream))

    def set_param(self, param_name, param_value, param_type = common.MAV_PARAM_TYPE_UINT8):
        connection = self.get_connection()
        connection.mav.param_set_send(connection.target_system, connection.target_component, param_name, param_value, param_type)
        

    async def send_command(self, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0):
        await self.message_stream.send_command(command=command, 
                                               param1=param1, param2=param2, param3=param3, param4=param4, param5=param5,param6=param6, param7=param7)
    
    async def get_home_position(self):
        while True:
            if(len(self.home_position)>2):
                break
            await asyncio.sleep(0.5)
        
        return self.home_position
    
    def get_connection(self):
        return self.connection

    def get_queue(self):
        return self.message_queue
    
    def get_message_stream(self):
        return self.message_stream