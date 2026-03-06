import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone, DroneProperties
from utils.mission import Mission

from utils.logger import log_success, log_system, log_fail
from utils.takeoff import takeoff,return_to_launch
import utils.mode as mode
from helper.file_reader import read_waypoints

class WaypointNavigation:
    def __init__(self, drone: Drone, waypointsFile = None):
        self.drone = drone
        pass

    async def get_sorted_waypoints(self, waypoints = None):
        pass

    async def upload_mission(self, waypointsFile = None):
        waypoints = read_waypoints(waypointsFile) if waypointsFile else None



