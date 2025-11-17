from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
from messages import MessageStream
from logger import logger

class Drone:

    home_position = {'lat': 0, 'long': 0, 'alt': 0}

    def __init__(self):
        self.message_queue = asyncio.Queue()
        self.home_position = {}

    def connect_drone(self,connection_string = 'tcp:127.0.0.1', port = 5763, baud = 57600):
        self.connection = mavutil.mavlink_connection(f'{connection_string}:{port}', baud)
        self.connection.wait_heartbeat()
        print(f"Connected to {connection_string} on port {port} with system id {self.connection.target_system} and component id {self.connection.target_component}")
        
    def set_message_stream(self, message_stream):
         self.message_stream = message_stream

    async def start_processes(self, stream: asyncio.Queue):
        await logger(stream)

    async def set_home_position(self):
        gps = await self.message_stream.request_message(common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT)
        
        self.home_position['lat'] = gps.lat
        self.home_position['long'] = gps.lon
        self.home_position['alt'] = gps.relative_alt
        print(self.home_position)



    
            

    def get_home_position(self):
        return self.home_position
    
    def get_connection(self):
        return self.connection

    def get_queue(self):
        return self.message_queue