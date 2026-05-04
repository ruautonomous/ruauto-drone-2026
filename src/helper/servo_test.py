import asyncio
from pymavlink.dialects.v20 import common
from pymavlink import mavutil

from utils.drone import Drone

# FOR servo_num, 1-8 is for the MAIN channels 1-8 and 9-16 is for AUX channels
# we'll use MAIN channels since the AUX channels are used for ESCs

# WHEN THE SERVOS NEED TO BE STOPPED, CHANGE ITS PWM TO THE SERVO TRIM VALUE WHICH IS 1500us for our diymall servos
# check what your servos trim value needs to be and also configure it in ardupilot parameters (SERVO[X]_TRIM)

SERVO_MAX = 2200
SERVO_MIN = 600
SERVO_MIN_DROP = 1000
SERVO_MAX_DROP = 2000
SERVO_TRIM = 1500

async def set_servo(drone: Drone, servo_num: int = 0, servo_value: int = 1000, sleep_wait = 5):
    ack = await drone.send_command(command=common.MAV_CMD_DO_SET_SERVO, param1=servo_num, param2=servo_value)
    await asyncio.sleep(sleep_wait)

async def servo_open_close(drone: Drone, servo_num = 1, servo_value = 1000):
    await set_servo(drone=drone, servo_num=servo_num, servo_value=servo_value, sleep_wait=3)
    await set_servo(drone=drone, servo_num=servo_num, servo_value=SERVO_TRIM, sleep_wait=0)

async def test_servo(drone: Drone, servo_num: int = 0, servo_value: int = 1000):
    ack = await drone.send_command(command=common.MAV_CMD_DO_SET_SERVO, param1=servo_num, param2=servo_value)
    await asyncio.sleep(4)  
    pass

async def full_spin_servo(drone, servo_num):
    await test_servo(drone, servo_num, 2500)
    await test_servo(drone, servo_num, 500)
    await test_servo(drone, servo_num, 1500)

async def unravel_spool(drone, servo_num, sleep = 5):
    await set_servo(drone=drone, servo_num=servo_num, servo_value=(1.1*SERVO_TRIM), sleep_wait=sleep)
    await set_servo(drone=drone,servo_num=servo_num, servo_value=SERVO_TRIM) 
    # i believe since 360 servos, the value determines speed and dir in which they spin, not a position, going 10% above trim should 
    # spin the servo one way at a fair speed
