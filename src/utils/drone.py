# base imports
import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

# util imports
from utils.messages import MessageStream

# etc imports
from io.file_reader import read_config_file

class Drone:
    def __init__(self):
        self.handler = MessageStream()
        print('initializing drone')

    def handle_msg(self):
        pass

    def initialize_params(self, parametersFile = None):
        '''Reads the drone settings file and initializes parameters to Drone instance. Called by default constructor'''
        params = read_config_file(parametersFile) if parametersFile else -1
        print(params)
        self.target_alt = int(params['altitude']) if parametersFile else 10
        self.threshhold = float(params['threshhold']) if parametersFile else 2
        self.threshholdZ = float(params['threshholdZ']) if parametersFile else 1
        self.climbspeed = int(params['climbspeed']) if parametersFile else -2
        self.airspeed = int(params['airspeed']) if parametersFile else -2
        self.servo_num = int(params['servo_num']) if parametersFile else -1
        self.square_size = int(params['square_size']) if parametersFile else 1

    async def send_heartbeat():
        pass

    