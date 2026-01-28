from drone import Drone
from pymavlink.dialects.v20 import common 
import asyncio
# from mission import Mission
# from modes import Modes
from messages import MessageStream 
from geofence import Fence
import utils.file_reader as file_reader
from logger import log_system, bcolors
from missions import waypointnavigation, circuittimetrial, packagedelivery, packagedrop, packagerecovery, targetlocalization

config = file_reader.read_config_file()
waypoints = file_reader.read_waypoints()
geofence_points = file_reader.read_geofence('info_files/testingfence.txt')

# print(config)
print(waypoints)
# print(geofence_points)

drone = Drone('info_files/params.txt')
drone.connect_drone(config['connection'])

connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)

# mission = Mission(drone, waypoints)
# modes = Modes(drone)
fence = Fence(drone)


async def mission_picker(input, drone, waypoints):
    """
    Used to execute the mission that is defined in the config.txt
    """
    print(f'INPUT IS {input}')
    match(int(input)):
        case 1: # Waypoint Navigation
            waypointNav = waypointnavigation.WaypointNav(drone, waypoints)
            print('BEGINNING SETUP')
            await waypointNav.begin_setup()
        case 2: # Circuit Time Trial
            trial = circuittimetrial.CircuitTimeTrial(drone, waypoints)
            await trial.begin_mission()
        case 3: # Package Drop
            pass
        case 4: # Package Delivery
            pass
        case 5: # Target Localization
            pass
        case 6: # Package Recovery
            pass
        case _:
            log_system(msg="Unknown Mission?", msgname="ERROR", color=bcolors.FAIL)

async def main():
    print('running')
    
    await asyncio.gather(drone.start_processes(msg_stream.stream), fence.upload_fence(geofence_points), mission_picker(config['mission'], drone, waypoints))

# TO DO
# 1) Change the upload_mission() function in missions.py to have the drone go to the altitude specified insteam of the 'target_alt'

asyncio.run(main())




