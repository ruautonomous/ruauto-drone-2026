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
from helper.file_reader import read_config_file

class PackageRecovery:
    
    def __init__(self, drone: Drone, initFile = None):
        self.drone = drone
        self.file = initFile
        config = read_config_file(file=initFile) if initFile else None
        self.config = config

        # getting pickup lat long
        pickup_loc: str = config['pickup_loc'] 
        pickup_loc = pickup_loc.removesuffix('\n').split(',')
        self.pickup_loc = [float(pickup_loc[0]), float(pickup_loc[1])]

    async def upload_mission(self, rtl:bool = True):
        server_sock = self.start_listener()
        self.server_sock = server_sock
        self.baseline = await self.set_baseline()
        await takeoff(drone=self.drone, target_alt=self.drone.target_alt)
        await reposition_drone_deg(drone=self.drone, coordinates=self.pickup_loc)
        await self.turn_hook()
        pass
    
    async def turn_hook(self):
        '''note to self: on the claw mechanism, put a piece of tape next to every servo and write the channel number it goes to'''
        asyncio.gather(
        await set_servo(drone=self.drone, servo_num=1, servo_value=1.3*SERVO_TRIM, sleep_wait=0),
        await set_servo(drone=self.drone, servo_num=3, servo_value=0.7*SERVO_TRIM, sleep_wait=0)
        )
        await asyncio.sleep(2)
        asyncio.gather(
        await reset_servo(drone=self.drone, servo_num=1),
        await reset_servo(drone=self.drone, servo_num=3)
        )

        pass
    
    async def set_baseline(self, num_reading: int = 3):
        '''To be used at start of mission when there is NO load in the recovery mechanism. Takes num_reading number of readings and averages them to
        set a baseline load cell reading that designates the no load value. Done this way so that an abnormal reading at the beginning of the mission 
        does not screw up the entire system'''
        readings = []
        for i in range(num_reading):
            read = await self.get_current_weight(self.server_sock)
            if read == None:
                i-=1
            readings.append(read)

        average = 0
        for reading in readings:
            average += reading
        
        log_system(msgname="Load Cell Manager", msg=f"Setting baseline load cell value. Readings used: {readings}")
        return (average/readings.__len__())
    def start_listener():
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(False)
        # Set a timeout so your main app doesn't freeze if the scale script stops
        sock.settimeout(0.5)
        return sock

    async def get_current_weight(sock: socket.socket):
        """Fetches the most recent broadcasted weight. If after 31 x 0.2 = 6.2 seconds, no data recieved it errors"""
        i=0
        while True:
            try:
                # Buffer size of 1024 bytes is plenty for a simple number

                data, addr = sock.recvfrom(1024) 
                i=0
                # Decode the bytes back into a float/int
                return float(data.decode('utf-8'))
            except socket.timeout or BlockingIOError:
                i += 1
                if i == 31:
                    print("Warning: No data received from scale broadcaster.")
                    return None
                await asyncio.sleep(0.2)
                