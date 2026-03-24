import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone, DroneProperties
import utils.mode as mode
from utils.mission import Mission
from utils.armdisarm import arm_drone

from helper.file_reader import read_waypoints

class CircuitTimeTrial:
    def __init__(self, drone: Drone, waypointsFile: str = None):
        self.drone = drone
        self.custom_points = read_waypoints(waypointsFile) if waypointsFile else None
        self.mission_handler = Mission(waypointsFile=waypointsFile)
        pass

    async def upload_mission(self, waypointsFile = None):
        waypoints = read_waypoints(waypointsFile) if waypointsFile else None
        if self.custom_points is not None:
            waypoints = self.custom_points
        await self.mission_handler.upload_mission(waypoints=waypoints, begin_immediately=False)
        await self.mission_handler.begin_mission(rtl=False)