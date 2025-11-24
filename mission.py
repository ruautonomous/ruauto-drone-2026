from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
from drone import Drone

class Mission:
    
    
    def __init__(self, drone: Drone, points: list = [[0,0]]):
        self.drone = drone
        self.points = points
        self.mission_setup()
        pass
    
    def mission_setup(self):
        if not self.drone is None:
            connection = self.drone.get_connection()
            connection.mav.mission_clear_all_send(connection.target_system, connection.target_component)
        pass

    async def upload_mission(self, waypoints: list):
        
        pass