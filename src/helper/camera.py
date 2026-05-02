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

connection = mavutil.mavlink_connection('/dev/ttyTHS1')
connection.wait_heartbeat()
print('connected')

pitch = 25
while pitch != -91:
    connection.mav.command_long_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL,
        1,
        float(pitch), # pitch
        0.0,
        0.0,
        0,0,0,2
    )
    ack = connection.recv_match(type="COMMAND_ACK", blocking=True)
    print(ack)
    pitch -= 5