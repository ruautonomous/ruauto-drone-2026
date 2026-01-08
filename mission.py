from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
from drone import Drone
from logger import log_custom

class Mission:
    
    
    def __init__(self, drone: Drone, points: list = [[0,0]]):
        
        self.drone = drone
        self.points = points
        pass
    
    def mission_setup(self, waypoints):
        connection = 0
        if not self.drone is None:
            connection = self.drone.get_connection()
            connection.mav.mission_clear_all_send(connection.target_system, connection.target_component, common.MAV_MISSION_TYPE_MISSION)
            log_custom("Mission Cleared")
        
        # if(len(self.points) > 1):
        #     waypoints = self.points

        clean_points = []
        for wp in waypoints:
            if wp[0] < 1e5 and wp[1] < 1e5:
                clean_points.append([
                    (int)(wp[0]*1e7), # lat
                    (int)(wp[1]*1e7)])# long
            else:
                clean_points.append(wp)
        return clean_points

        
    async def get_mission_items(self, waypoints: list = None):
        if waypoints is None:
            waypoints = self.points
        connection = self.drone.get_connection()

        while True:
            home_pos = self.drone.get_home_position()
            # print(f'HOME POS IS {home_pos} with len {len(home_pos)}')
            if len(home_pos) > 0:
                break
            await asyncio.sleep(0.1)

        log_custom(f'HOME POS: {home_pos}', important=True)
        encoded_commands = []
        encoded_commands.append(connection.mav.mission_item_int_encode(
            connection.target_system, connection.target_component, 0, common.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, common.MAV_CMD_NAV_TAKEOFF, 1, 1,
            0,0,0,0,(int)(home_pos['lat']),(int)(home_pos['long']),self.drone.target_alt, common.MAV_MISSION_TYPE_MISSION
        ))
        for i,wp in enumerate(waypoints,start=1):
            encoded_commands.append(connection.mav.mission_item_int_encode(
                connection.target_system,connection.target_component, i, common.MAV_FRAME_GLOBAL_RELATIVE_ALT, common.MAV_CMD_NAV_WAYPOINT, 0, 1,
                0,0,0,0,wp[0],wp[1],self.drone.target_alt, common.MAV_MISSION_TYPE_MISSION
            ))

        encoded_commands.append(connection.mav.mission_item_int_encode(
            connection.target_system,connection.target_component, self.mission_length-1, common.MAV_FRAME_GLOBAL_TERRAIN_ALT, common.MAV_CMD_NAV_LAND, 0,1,
            0,0,0,0,home_pos['lat'], home_pos['long'], home_pos['alt'], common.MAV_MISSION_TYPE_MISSION))
        
        return encoded_commands

    async def upload_mission(self, waypoints: list = [0,0]):
        
        if not self.points == [[0,0]] and waypoints == [0,0]:
            waypoints = self.points

        # print('Mission Upload Sequence Beginning')
        waypoints = self.mission_setup(waypoints)
        connection = self.drone.get_connection()
        
        self.mission_length = len(waypoints) + 2
        mission_items = await self.get_mission_items(waypoints=waypoints)

        log_custom(f'SENDING MISSION COUNT OF {self.mission_length}')
        connection.mav.mission_count_send(connection.target_system,connection.target_component, self.mission_length, common.MAV_MISSION_TYPE_MISSION)

        request = await self.drone.message_stream.wait_for_message('MISSION_REQUEST','MISSION_REQUEST_INT')
        connection.mav.send(mission_items.pop(0))

        for i,wp in enumerate(waypoints, start=1):
            request = await self.drone.message_stream.wait_for_message('MISSION_REQUEST','MISSION_REQUEST_INT')
            log_custom(f'SENDING {wp}')
            connection.mav.send(mission_items.pop(0))

        request = await self.drone.message_stream.wait_for_message('MISSION_REQUEST','MISSION_REQUEST_INT')
        log_custom(f'mission request {request.seq}. Sending RTL Command')
        connection.mav.send(mission_items.pop(0))
        mission_ack = await self.drone.message_stream.wait_for_message('MISSION_ACK')
        log_custom(f'FLIGHT PLAN UPLOADED: {mission_ack}', important=True) # remove this if log becomes cluttered
        pass