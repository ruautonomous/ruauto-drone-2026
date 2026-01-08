from drone import Drone
from pymavlink.dialects.v20 import common 
import asyncio
# from mission import Mission
# from modes import Modes
from messages import MessageStream 
from geofence import Fence
import utils.file_reader as file_reader
from missions.waypointnavigation import WaypointNav

config = file_reader.read_config_file()
waypoints = file_reader.read_waypoints()
geofence_points = file_reader.read_geofence('info_files/testingfence.txt')

# print(config)
print(waypoints)
# print(geofence_points)

drone = Drone('info_files/params.txt')
drone.connect_drone()


connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)

# mission = Mission(drone, waypoints)
# modes = Modes(drone)
fence = Fence(drone)
waypointNav = WaypointNav(drone, waypoints)
async def main():
    print('running')
    
    await asyncio.gather(drone.start_processes(msg_stream.stream), fence.upload_fence(geofence_points), waypointNav.begin_setup())
                        #  , mission.upload_mission(), modes.rtl())


asyncio.run(main())



