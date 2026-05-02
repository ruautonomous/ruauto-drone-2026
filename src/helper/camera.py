# import asyncio 
from pymavlink import mavutil 
from pymavlink.dialects.v20 import common
# import cv2

# from utils.drone import Drone


# class Camera:
#     def __init__(self, drone: Drone):
#         self.drone = drone
#         pass

#     def connect_camera(self):
#         cam = cv2.VideoCapture(self.drone.camera_url)
    
'''supposedly this will be handled by imaging'''
import time
def main():
    connection = mavutil.mavlink_connection('/dev/ttyTHS1')
    connection.wait_heartbeat()
    print('connected')

    #test_pitch(connection)
    test_yaw(connection)
    #test_roll(connection)

def test_pitch(connection):
    pitch = 25
    while pitch != -95:
        print(f'pitch = {pitch} deg')
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL,
            1,
            float(pitch), # pitch
            0.0, # roll
            0.0, # yaw
            0,0,0,2
        )
        ack = connection.recv_match(type="COMMAND_ACK", blocking=True)
        print(ack)
        pitch -= 5
        time.sleep(1.5)

def test_yaw(connection):
    yaw = 135
    while yaw != -140:
        print(f'yaw = {yaw} deg')
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL,
            1,
            0, # pitch
            0.0, # roll
            float(yaw), # yaw
            0,0,0,2
        )
        ack = connection.recv_match(type="COMMAND_ACK", blocking=True)
        print(ack)
        yaw -= 5
        time.sleep(1.5)

def test_roll(connection):
    yaw = 30
    while yaw != -35:
        print(f'roll = {yaw} deg')
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL,
            1,
            0, # pitch
            float(yaw), # roll
            0, # yaw
            0,0,0,2
        )
        ack = connection.recv_match(type="COMMAND_ACK", blocking=True)
        print(ack)
        yaw -= 5
        time.sleep(1.5)
        
main()
