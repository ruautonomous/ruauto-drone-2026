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

import cv2
import numpy as np
import time
from typing import Tuple, Optional

class PackageDrop:

    def __init__(self, drone: Drone, file):
        self.drone = drone
        config = read_config_file(file=file)
        self.config = config
        self.takeoff_alt = float(config["takeoff_alt"])
        self.drop_alt = float(config["drop_alt"])
        drop_loc: str = config['drop_loc'] 
        drop_loc = drop_loc.removesuffix('\n').split(',')
        self.drop_loc = [float(drop_loc[0]), float(drop_loc[1])]
        
        # Bullseye mission constants
        self.MIN_ALT_METERS = 15
        self.PIXEL_TOLERANCE = 20
        self.GAIN = 0.002
        self.MAX_VEL = 1.0
        pass

    async def upload_mission(self, rtl: bool = True):
        asyncio.create_task(self.camera())
        asyncio.create_task(self.movement_mission(rtl))
        pass

    async def movement_mission(self, rtl: bool = True):
        await takeoff(drone=self.drone, target_alt = self.takeoff_alt)
        await reposition_drone_deg(drone=self.drone, coordinates = self.drop_loc)
        print(f'DROP LOC IS {self.drop_loc}')
        await self.drop_package()
        if rtl:
            await return_to_launch(drone=self.drone)

    def detect_bullseye(self, image) -> Optional[Tuple[int, int, int]]:
        """
        Detect bullseye center using concentric circles
        Returns: (x, y, radius) of the detected bullseye, or None if not found
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Blur to reduce noise
        gray = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=100,
            param1=100,
            param2=30,
            minRadius=20,
            maxRadius=0
        )
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            
            # If multiple circles detected, find the center of concentric circles
            if len(circles[0]) > 1:
                centers = [(circle[0], circle[1]) for circle in circles[0]]
                # Average center for concentric circles
                cx = int(np.mean([c[0] for c in centers]))
                cy = int(np.mean([c[1] for c in centers]))
                # Use radius of the largest circle
                radius = max([circle[2] for circle in circles[0]])
                return (cx, cy, radius)
            else:
                # Single circle detected
                x, y, r = circles[0][0]
                return (x, y, r)
        
        return None

    async def camera(self):
        cam_id = 0

        # Initialize capture
        # We try V4L2 first as it's standard for the SIYI A8 Mini
        cap = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)

        # Set the resolution to match your SIYI output
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not cap.isOpened():
            print(f"Error: Could not open camera at /dev/video{cam_id}")
            exit()

        print("Stream Started. Press 'q' to exit.")

        while True:
            ret, frame = cap.read()
            self.set_camera_frame(frame)
            if not ret:
                print("Empty frame received. Check connections.")
                break
            await asyncio.sleep(1)
 
    def calculate_movement_to_center(self, target_x, target_y, frame_width, frame_height):
        """
        Calculate velocity commands to center drone on target
        Returns: (vx, vy, vz, is_centered) - velocity commands and centering status
        """
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2
        
        error_x = target_x - frame_center_x
        error_y = target_y - frame_center_y
        
        print(f"Error X: {error_x}, Error Y: {error_y}")
        
        # Check if centered within tolerance
        is_centered = (abs(error_x) < self.PIXEL_TOLERANCE and 
                      abs(error_y) < self.PIXEL_TOLERANCE)
        
        if is_centered:
            return (0, 0, 0, True)
        
        # Apply deadband to prevent oscillation
        if abs(error_x) < self.PIXEL_TOLERANCE:
            error_x = 0
        if abs(error_y) < self.PIXEL_TOLERANCE:
            error_y = 0
        
        # Convert to velocity commands
        vx = -error_y * self.GAIN  # forward/back (NED frame)
        vy = -error_x * self.GAIN  # left/right (NED frame)
        vz = 0  # hold altitude by default
        
        # Clamp velocities to maximum
        vx = max(min(vx, self.MAX_VEL), -self.MAX_VEL)
        vy = max(min(vy, self.MAX_VEL), -self.MAX_VEL)
        
        return (vx, vy, vz, False)

    def stop_movement_when_centered(self, is_centered):
        """
        Stop drone movement when centered on target
        Returns: True if mission should continue, False if complete
        """
        if is_centered:
            # Send zero velocity command to stop movement
            self.drone.master.mav.set_position_target_local_ned_send(
                0,
                self.drone.master.target_system,
                self.drone.master.target_component,
                mavutil.mavlink.MAV_FRAME_BODY_NED,
                0b0000111111000111,  # velocity only
                0, 0, 0,
                0, 0, 0,  # zero velocities
                0, 0, 0,
                0, 0
            )
            print("Drone centered on target - movement stopped")
            return False
        
        return True

    def set_camera_frame(self, frame):
        self.newest_frame = frame

    def _get_camera_frame(self):
        """
        Placeholder for camera frame acquisition
        You need to implement this based on your camera setup
        """
        return self.newest_frame
        # Example implementation:
        # return your_camera.get_frame()
        pass

    async def bullseye_mission(self):
        # -*- coding: utf-8 -*-
        """opencv bullseye detection
        Processes the current frame to detect the bullseye and adjust drone velocity.
        Returns True if the drone is successfully centered, False otherwise.
        """
        # Camera/frame parameters
        frame_width = 640
        frame_height = 480
    
        try:
            # 1. DETECTION PHASE - Detect bullseye using concentric circles
            frame = self._get_camera_frame()
        
            if frame is None:
                print("No camera frame available")
                return False
        
            detection_result = self.detect_bullseye(frame)
        
            if detection_result is None:
                print("No bullseye detected")
                return False
        
            target_x, target_y, radius = detection_result
            print(f"Bullseye detected at: ({target_x}, {target_y}), radius: {radius}")
        
            # 2. MOVEMENT PHASE - Calculate movement using detected center
            current_alt = self.drone.get_altitude()
            vx, vy, vz, is_centered = self.calculate_movement_to_center(
                target_x, target_y, frame_width, frame_height
            )
        
            # Altitude safety check
            if current_alt < self.MIN_ALT_METERS:
                vz = -0.5  # ascend slightly
        
            # 3. STOPPING PHASE - Stop when drone reaches center within tolerance
            if not self.stop_movement_when_centered(is_centered):
                print("Mission complete - drone centered on bullseye!")
                return True
        
            # Send movement commands if not centered
            self.drone.master.mav.set_position_target_local_ned_send(
                0,
                self.drone.master.target_system,
                self.drone.master.target_component,
                mavutil.mavlink.MAV_FRAME_BODY_NED,
                0b0000111111000111,  # velocity only
                0, 0, 0,
                vx, vy, vz,
                0, 0, 0,
                0, 0
            )
            
            return False
        except KeyboardInterrupt:
            print("Mission interrupted by user")
            self.stop_movement_when_centered(True)  # Force stop
        except Exception as e:
            print(f"Error in bullseye mission: {e}")
            self.stop_movement_when_centered(True)  # Force stop
            return False


    async def drop_package(self, servo_num = 1, servo_value = SERVO_MIN_DROP):
        log_system(msgname="DROPPING PACKAGE", msg=f"Dropping package")
        await servo_open_close(drone=self.drone, servo_num=servo_num, servo_value=servo_value)
        log_system(msgname="DROPPED PACKAGE", msg=f"Hopefully it dropped :pray:")
        pass
