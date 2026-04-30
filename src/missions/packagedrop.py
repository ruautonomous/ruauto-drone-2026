import asyncio 
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.takeoff import *
from utils.armdisarm import *
from utils.reposition import *
import utils.mode as mode
from helper.servo_test import *
from helper.file_reader import read_config_file

class PackageDrop:

    def __init__(self, drone: Drone, file):
        self.drone = drone
        config = read_config_file(file=file)
        self.config = config
        self.takeoff_alt = float(config["takeoff_alt"])
        self.drop_alt = float(config["drop_alt"])

        pass

    async def upload_mission(self):
        # await takeoff(drone=self.drone, target_alt = self.takeoff_alt)
        
        pass

    async def drop_package(self, servo_num = 1, servo_value = SERVO_MIN_DROP):
        log_system(msgname="DROPPING PACKAGE", msg=f"Dropping package")
        await servo_open_close(drone=self.drone, servo_num=servo_num, servo_value=servo_value)
        log_system(msgname="DROPPED PACKAGE", msg=f"Hopefully it finished dropped")
        pass
