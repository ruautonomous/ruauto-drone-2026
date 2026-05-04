import asyncio 
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.takeoff import *
from utils.armdisarm import *
from utils.reposition import *
import utils.mode as mode
from helper.gimbal import reposition_gimbal
from helper.file_reader import read_config_file
from helper.servo_test import *

class PackageDelivery:
    
    def __init__(self, drone: Drone, initFile = None):
        self.drone = drone
        self.file = initFile
        config = read_config_file(file=initFile) if initFile else None
        self.alt = 4 # 4 meters 

        self.config = config
        self.drop_alt = float(config["drop_alt"])
        drop_loc: str = config['drop_loc'] 
        drop_loc = drop_loc.removesuffix('\n').split(',')
        self.drop_loc = [float(drop_loc[0]), float(drop_loc[1])]

        try:
            self.servos = [(str(config['servos'])).removesuffix('\n').split(',')[0],(str(config['servos'])).removesuffix('\n').split(',')[1]]
            print(f'servo nums for package delivery are {self.servos}')
            # shitty code. im writing this at night i hope it works lol 
        except:
            self.servos = [1,2]

    async def upload_mission(self, rtl:bool = True):
        #await takeoff(drone=self.drone, target_alt=self.alt) 
        #await reposition_gimbal(drone=self.drone, pitch=-90)
        #await reposition_drone_deg(drone=self.drone, coordinates=self.drop_loc)
        '''IMAGING CODE HERE!!!'''
        await self.drop_spool(servos=None, sleep_time=60) # allowing 60 seconds to unravel spool. change this if tests are done
        '''
        if rtl:
            await return_to_launch(self.drone)
        pass
        '''

    async def drop_spool(self, servos, sleep_time=10, percent: int = 30):
        for i,servo in enumerate(servos):
            asyncio.create_task(unravel_spool(drone=self.drone, servo_num=servo, sleep=sleep_time, percentage=percent, opposite=(i%2==1)))