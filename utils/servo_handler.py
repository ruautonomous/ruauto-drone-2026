# This file is used to control the servo as needed. 

import asyncio
from drone import Drone
from pymavlink.dialects.v20 import common


class ServoHandler:
    def __init__(self, drone: Drone, servo_num):
        self.drone = drone
        self.servo_num = servo_num

    async def open_servo(self):
        pass

    async def close_servo(self):
        pass
    
    async def custom_servo_pos(self, pwm_value):
        pass