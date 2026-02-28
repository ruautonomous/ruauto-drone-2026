from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio

from drone import Drone
from logger import log_system, bcolors

from helper.file_reader import read_waypoints

class Mission:
    def __init__(self, drone: Drone, waypointsFile = 'info_files/waypoints.txt'):
        self.drone = drone
        self.waypoints = read_waypoints(waypointsFile)