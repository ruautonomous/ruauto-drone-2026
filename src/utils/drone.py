# base imports
import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

# util imports
from utils.messages import MessageStream
from utils.logger import bcolors, log_system

# etc imports
from helper.file_reader import read_config_file

class Drone:
    def __init__(self):
        print('initializing drone')


    def retrieve_configuration(self, parametersFile = None, configFile = None):
        '''Reads the drone settings file and initializes parameters to Drone instance'''
        params = read_config_file(parametersFile) if parametersFile else -1
        print(params)
        self.target_alt = int(params['altitude']) if parametersFile else 10
        self.threshhold = float(params['threshhold']) if parametersFile else 2
        self.threshholdZ = float(params['threshholdZ']) if parametersFile else 1
        self.climbspeed = int(params['climbspeed']) if parametersFile else -2
        self.airspeed = int(params['airspeed']) if parametersFile else -2
        self.servo_num = int(params['servo_num']) if parametersFile else -1
        self.square_size = int(params['square_size']) if parametersFile else 1

        if(configFile):
            self.config = read_config_file(configFile)

    def connect_drone(self,connection_string = 'tcp:127.0.0.1:5763', port = False):
        '''This method is used to connect to the drone given the connection string'''
        print(connection_string)
        self.connection: mavutil.mavtcp = mavutil.mavlink_connection(device=connection_string) # specifying baud rate breaks everything
        self.connection.wait_heartbeat()
        log_system(msg=f"{bcolors.HEADER} -- Connected to {connection_string} on port {port if port else "NO PORT"} with system id {self.connection.target_system} and component id {self.connection.target_component} --{bcolors.ENDC}", color=bcolors.SUCCESS)
        self.message_stream = MessageStream(self.connection)
        # while True:
        #     print(self.connection.recv_match(blocking=True))
        
    def initialize_drone(self, parametersFile, configFile):
        self.retrieve_configuration(parametersFile,configFile)
        self.connection_str: str = self.config[DroneProperties.CONNECTION]
        try:
            if(self.connection_str.__contains__(':')):
                self.port = self.connection_str[self.connection_str.index(':')]
            else:
                self.port = False
        except Exception: 
            print('exception idk in intialize_drone() in drone.py')
        
        self.connect_drone(connection_string=self.connection_str, port=self.port)


    async def send_heartbeat(self):
        while True:
            self.get_connection().mav.heartbeat_send(common.MAV_TYPE_GCS, common.MAV_AUTOPILOT_INVALID, 0,0,0)
            log_system(msg="Sent heartbeat to drone from GCS")
            await asyncio.sleep(1)

    async def send_command(self, command, 
                           param1 = 0, param2 = 0, param3 = 0, param4 = 0, param5 = 0, param6 = 0, param7 = 0, timeout = 5):
        return await self.message_stream.send_command(command=command, param1=param1, param2=param2, param3=param3, param4=param4,
                                                                          param5=param5, param6=param6, param7=param7, timeout=timeout)

    async def start_background_processes(self):
        await asyncio.create_task(self.message_stream.message_stream())
        await asyncio.create_task(self.send_heartbeat())
        await asyncio.create_task(self.message_stream.watch_for_heartbeat())   
        
    # GETTERS

    def get_connection(self):
        return self.connection

class DroneProperties:

    CONNECTION = 'connection'
    BAUD = 'baud'
    MISSION = 'mission'
