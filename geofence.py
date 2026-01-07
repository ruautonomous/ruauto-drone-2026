from pymavlink import mavutil 
from pymavlink.dialects.v20 import common
from drone import Drone
from logger import log_custom
import asyncio 
# https://ardupilot.org/copter/docs/common-geofencing-landing-page.html

class Fence:
    def __init__(self, drone: Drone, points: list = [[0,0]]):
        self.drone = drone
        self.points = points

    async def configure_fence(self):
        self.drone.set_param(b'FENCE_ACTION', 1)
        await self.drone.send_command(common.MAV_CMD_DO_FENCE_ENABLE, param1=1)
        self.drone.get_connection().mav.mission_clear_all_send(
            self.drone.get_connection().target_system,
            self.drone.get_connection().target_component,
            common.MAV_MISSION_TYPE_FENCE
        )
        log_custom('Fence Cleared')
        

    def clean_points(self,points: list = [[0,0]]):
        newPoints = []
        for point in points:
            if(point[0] < 1e5 and point[1] < 1e5):
                newPoints.append( [(int)(point[0] * 1e7), (int)(point[1]*1e7)] )
            else:
                newPoints.append([point[0], point[1]])
        
        return newPoints

    async def upload_fence(self, points: list = [[0,0]]):
        await self.configure_fence()
        if(len(self.points) == 1):
            self.points = points
        connection = self.drone.get_connection()
        connection.mav.mission_count_send(connection.target_system,connection.target_component,len(points), common.MAV_MISSION_TYPE_FENCE, 0)
        log_custom(f'Sending fence length of {len(points)} | Waiting for mission request')

        points = self.clean_points(points)
        
        print(points)
        for i,point in enumerate(points, start=0):
            await self.drone.get_message_stream().wait_for_message('MISSION_REQUEST', 'MISSION_REQUEST_INT')
            connection.mav.mission_item_int_send(connection.target_system,connection.target_component, i, common.MAV_FRAME_GLOBAL_INT, common.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION,
                                                 0, 1, len(points), 0,0,0, point[0], point[1], 0, common.MAV_MISSION_TYPE_FENCE)
            log_custom(f'Sending Fence Item {i}', important=True)
            
        
