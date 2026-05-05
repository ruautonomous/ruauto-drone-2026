import asyncio 
import socket
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.takeoff import *
from utils.armdisarm import *
from utils.reposition import *
import utils.mode as mode

from helper.servo_test import *

class PackageRecovery:
    
    def __init__(self, drone: Drone, initFile = None):
        self.drone = drone
        self.file = initFile

    async def upload_mission(self, rtl:bool = True):
        #server_sock = self.start_listener()
        #current_weight = self.get_current_weight(server_sock)
        await self.turn_hook()
        pass
    
    async def turn_hook(self):
        await asyncio.gather(
            set_servo(drone=self.drone, servo_num=1, servo_value=1.3*SERVO_TRIM, sleep_wait=2),
            set_servo(drone=self.drone, servo_num=3, servo_value=0.7*SERVO_TRIM, sleep_wait=2)
            )
        await asyncio.gather(
            set_servo(drone=self.drone, servo_num=1, servo_value=SERVO_TRIM, sleep_wait=2),
            set_servo(drone=self.drone, servo_num=3, servo_value=SERVO_TRIM, sleep_wait=2)
            )
        pass
    
    def start_listener():
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        # Set a timeout so your main app doesn't freeze if the scale script stops
        sock.settimeout(0.5)
        return sock

    def get_current_weight(sock: socket.socket):
        """Fetches the most recent broadcasted weight."""
        try:
            # Buffer size of 1024 bytes is plenty for a simple number
            data, addr = sock.recvfrom(1024) 
            # Decode the bytes back into a float/int
            return float(data.decode('utf-8'))
        except socket.timeout:
            print("Warning: No data received from scale broadcaster.")
            return None