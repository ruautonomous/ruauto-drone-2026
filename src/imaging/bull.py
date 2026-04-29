import cv2
import numpy as np
from google.colab.patches import cv2_imshow
import pymavlink
from pymavlink import mavutil
import time
import math



def detect_bulleye(x,y):
    
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=100,
        param2=30,
        minRadius=10,
        maxRadius=200
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for x, y, r in circles[0]:
            print("Center:", x, y)
            print("Radius:", r)

    centers = []

    for circle in circles[0]:
        centers.append((circle[0], circle[1]))

    # Average center
    cx = int(np.mean([c[0] for c in centers]))
    cy = int(np.mean([c[1] for c in centers]))
    print("Final center:", (cx, cy))
    return cx, cy


from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import time
import math
 
cv2.imshow()


# --------------------------------
# CONNECT TO VEHICLE
# --------------------------------

master = mavutil.mavlink_connection('tcp:127.0.0.1:5763')

    # tcp:127.0.0.1:5763 is the connection string for the simulation (if 5763 doesnt work try 5760)
    # idk if its the same thing or something else for the software you're using

master.wait_heartbeat()
print("Connected to vehicle")
takeoff_alt = 5

def takeoff_drone():
    lat,long,alt = get_position()
    print(long)

    master.mav.command_long_send(master.target_system, master.target_component, common.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                               1, 0,0,0,0,0,0)

    msg = master.recv_match(type="COMMAND_ACK", blocking=True)
    print(msg)

    master.mav.command_long_send(master.target_system, master.target_component, common.MAV_CMD_DO_SET_MODE, 0,
                                    common.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4,0,0,0,0,0)


    msg = master.recv_match(type="COMMAND_ACK", blocking=True)
    print(msg)

    master.mav.command_long_send(master.target_system, master.target_component, common.MAV_CMD_NAV_TAKEOFF,0,
                                0,0,0,0, lat,long,takeoff_alt)

    while(True):
        current_alt = get_position()[2]
        if(current_alt < 0.95*takeoff_alt):
            print(current_alt)
            time.sleep(1)
        else:
            break

def land_drone():
    lat,long,alt = get_position()
    master.mav.command_long_send(master.target_system, master.target_component, common.MAV_CMD_NAV_LAND,0,
                                0,0,0,0, lat,long,0)
    while(True):
        current_alt = get_position()[2]
        if(current_alt > 0.05):
            print(current_alt)
            time.sleep(1)
        else:
            break

    master.mav.command_long_send(master.target_system, master.target_component, common.MAV_CMD_DO_SET_MODE, 0,
                                    common.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 0,0,0,0,0,0)


    msg = master.recv_match(type="COMMAND_ACK", blocking=True)
    print(msg)



#'''
# --------------------------------
# CONSTANTS
# --------------------------------
MIN_ALT_METERS = 15   # 30 feet
PIXEL_TOLERANCE = 20     # pixels deadband
GAIN = 0.002             # velocity scaling factor
MAX_VEL = 1.0            # m/s cap

# --------------------------------
# FUNCTION: Get Relative Altitude
# --------------------------------
def get_position():
    master.mav.command_long_send(master.target_system, master.target_component, common.MAV_CMD_REQUEST_MESSAGE, 0, common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
                                 0,0,0,0,0,0)
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    alt = msg.relative_alt / 1000.0
    pos = [msg.lat/1e7, msg.lon/1e7, alt]
    return pos
print(get_position())
# '''
# --------------------------------
# FUNCTION: Send Velocity Command (BODY FRAME)
# --------------------------------
def send_velocity_body(vx, vy, vz):
    master.mav.set_position_target_local_ned_send(
        0,
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b111111000111,  # velocity only - 0b0000111111000111
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0
    )

#'''
# --------------------------------
# MAIN CENTERING FUNCTION
# --------------------------------
def center_on_target(target_x, target_y, frame_width, frame_height):

    frame_center_x = frame_width // 2
    frame_center_y = frame_height // 2

    error_x = target_x - frame_center_x
    error_y = target_y - frame_center_y

    print("Error X:", error_x, "Error Y:", error_y)

    # Deadband (prevents oscillation)
    if abs(error_x) < PIXEL_TOLERANCE:
        error_x = 0
    if abs(error_y) < PIXEL_TOLERANCE:
        error_y = 0

    # Convert to velocity
    vx = -error_y * GAIN   # forward/back
    vy = -error_x * GAIN   # left/right
    vz = 0                 # hold altitude

    # Clamp velocity
    vx = max(min(vx, MAX_VEL), -MAX_VEL)
    vy = max(min(vy, MAX_VEL), -MAX_VEL)

    # Enforce minimum altitude
    current_alt = get_position()[2]
    if current_alt < MIN_ALT_METERS:
        vz = -0.5  # ascend slightly
    else:
        vz = 0

    send_velocity_body(vx, vy, vz)
#'''
# --------------------------------
# LOOP EXAMPLE
# --------------------------------

takeoff_drone()
print('takeoff complete')

while True:
     # Replace these with your OpenCV detected center
     
     frame = get_camera_frame()
     cx, cy = detect_bullseye(frame[0],frame[1])
     frame_width = 640
     frame_height = 480

     center_on_target(cx, cy, frame_width, frame_height)

     time.sleep(0.1)


# '''pitch, empty, empty, yaw, latitude, longtidude, altitude'''