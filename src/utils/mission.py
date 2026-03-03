from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio

from utils.drone import Drone, DroneProperties
from utils.logger import log_system, bcolors

from helper.file_reader import read_waypoints
import utils.mode as mode

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
    
    async def get_mission_items(self, waypoints: list = None):
        '''Encodes mission items using mission_item_int_encode, which returns an encoded mission item, that is appended to a list of mission items'''
        connection = self.drone.get_connection()
        # print('setting home pos')
        home_pos = await self.drone.get_home_position_int()
        
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
            connection.target_system,connection.target_component, len(waypoints)+1, common.MAV_FRAME_GLOBAL_TERRAIN_ALT, common.MAV_CMD_NAV_LAND, 0,1,
            0,0,0,0,home_pos['lat'], home_pos['long'], home_pos['alt'], common.MAV_MISSION_TYPE_MISSION))
        
        self.mission_length = len(encoded_commands)
        return encoded_commands
    
    async def upload_mission(self, waypoints = None, rtl: bool = True, begin_immediately = False):
        '''Uploads the mission to the drone after getting encoded mission items from get_mission_items(). The rtl boolean determines whether the land command
        is issued after all waypoints are uploaded. \nThis function first sends the number of mission items that are being sent, and waits for a MISSION_REQUEST message.
        Once recieved, it sends each encoded mission item, every time a MISSION_REQUEST is recieved. After all mission items sent, function waits for a MISSION_ACK'''
        self.waypoints = self.mission_setup(waypoints if waypoints else self.waypoints)
        mission_items = await self.get_mission_items(waypoints=self.waypoints)
        connection = self.drone.get_connection()

        if (not rtl):
            self.mission_length -= 1
            mission_items = mission_items.pop(len(mission_items)-1)
        
        log_system(msgname=DroneProperties.MISSION_HANDLER, msg=f"Sending mission type MISSION count of {self.mission_length}")
        connection.mav.mission_count_send(connection.target_system,connection.target_component, self.mission_length, common.MAV_MISSION_TYPE_MISSION)


        for i in range(self.mission_length+1):
            request = await self.drone.get_message_stream().wait_for_message('MISSION_REQUEST','MISSION_REQUEST_INT')
            log_system(msg=f"Sending mission index {i}", msgname=DroneProperties.MISSION_HANDLER, color=bcolors.MISSION)
            connection.mav.send(mission_items.pop(0))
        
        mission_ack = await self.drone.get_message_stream().wait_for_message("MISSION_ACK", secondary=common.MAV_MISSION_TYPE_MISSION)
        log_system(msgname=DroneProperties.MISSION_HANDLER, msg=f"Recieved Mission Ack: {mission_ack}", color=bcolors.MISSION)

        
        if(begin_immediately):
            mode.set_mode(self.drone, mode.AUTO)

