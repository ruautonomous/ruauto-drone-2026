from drone import Drone
from pymavlink.dialects.v20 import common 
import asyncio
from messages import MessageStream 
from geofence import Fence
import utils.file_reader as file_reader
from logger import log_system, bcolors
from missions import waypointnavigation, circuittimetrial, packagedelivery, packagedrop, packagerecovery, targetlocalization


'''
To-Do
- Package Drop
- Package Delivery
- Package Recovery
- MAV_CMD_DO_SET_SPEED has been failing whenever I try to change drone speed. Need to fix

To-Modify
- I want to completely redo the mission picker, I think its too rigid and relies solely on everything being done as a mission
- Edit Waypoint Nav 

'''



config = file_reader.read_config_file()
waypoints = file_reader.read_waypoints()
geofence_points = file_reader.read_geofence('info_files/testingfence.txt')

# print(config)
print(waypoints)
# print(geofence_points)

drone = Drone('info_files/settings.txt')
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
    multiple_mission = False

    if len(input) > 1:  # NEED TO EDIT READ_CONFIG_FILE TO STORE MULTIPLE MISSIONS IN AN ARRAY
        multiple_mission = True
        next_mission = input[1]
        input = input[0]

    print(f'INPUT IS {input}')
    match(int(input)):
        case 1: # Waypoint Navigation
            waypointNav = waypointnavigation.WaypointNav(drone, waypoints)
            await waypointNav.begin_setup(land=(not multiple_mission))
        case 2: # Circuit Time Trial
            trial = circuittimetrial.CircuitTimeTrial(drone, waypoints)
            await trial.begin_mission(land=(not multiple_mission))
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

    if multiple_mission:
        await mission_picker(next_mission)

async def main():
    print('running')
    
    await asyncio.gather(drone.start_processes(msg_stream.stream), fence.upload_fence(geofence_points), mission_picker(config['mission'], drone, waypoints))


asyncio.run(main())




