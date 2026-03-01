from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio

from utils.drone import Drone
from utils.logger import log_system, bcolors

from helper.file_reader import read_waypoints

class Mission:
    def __init__(self, drone: Drone, waypointsFile = 'info_files/waypoints.txt'):
        self.drone = drone
        self.waypoints = read_waypoints(waypointsFile)

    def mission_setup(self, waypoints):
        '''Clears current mission type MISSION and 'cleans' waypoints meaning it translates them to latitude/longitude if the waypoints are integers'''
        connection = self.drone.get_connection()
        connection.mav.mission_clear_all_send(connection.target_system, connection.target_component, common.MAV_MISSION_TYPE_MISSION)
        log_system(msgname="Mission Cleared", msg="MISSION PLANNER")
        
        clean_points = [] 
        for wp in waypoints:
            if wp[0] < 1e5 and wp[1] < 1e5:
                clean_points.append([
                    (int)(wp[0]*1e7), # lat
                    (int)(wp[1]*1e7), # long
                    wp[2] # altitude
                    ])
            else:
                clean_points.append(wp)
        return clean_points
    
    def get_mission_items(self, waypoints: list = None):
        '''Encodes mission items'''
        connection = self.drone.get_connection()
        home_pos = self.drone.get_home_position_int()
        
        log_system(msg=f'HOME POS: {home_pos}', msgname="Home Position")
        encoded_commands = []
        encoded_commands.append(connection.mav.mission_item_int_encode(
            connection.target_system, connection.target_component, 0, common.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, common.MAV_CMD_NAV_TAKEOFF, 1, 1,
            0,0,0,0,(int)(home_pos['lat']),(int)(home_pos['long']),self.drone.target_alt, common.MAV_MISSION_TYPE_MISSION
        ))
        for i,wp in enumerate(waypoints,start=1):
            print(f'WAYPOINT: {wp}')
            encoded_commands.append(connection.mav.mission_item_int_encode(
                connection.target_system,connection.target_component, i, common.MAV_FRAME_GLOBAL_RELATIVE_ALT, common.MAV_CMD_NAV_WAYPOINT, 0, 1,
                0,0,0,0,wp[0],wp[1],wp[2], common.MAV_MISSION_TYPE_MISSION
            ))

        encoded_commands.append(connection.mav.mission_item_int_encode(
            connection.target_system,connection.target_component, self.mission_length-1, common.MAV_FRAME_GLOBAL_TERRAIN_ALT, common.MAV_CMD_NAV_LAND, 0,1,
            0,0,0,0,home_pos['lat'], home_pos['long'], home_pos['alt'], common.MAV_MISSION_TYPE_MISSION))
        
        return encoded_commands
    
    async def upload_mission(self, waypoints = None):
        self.waypoints = self.mission_setup(waypoints if waypoints else self.waypoints)
        mission_items = self.get_mission_items(waypoints=self.waypoints)