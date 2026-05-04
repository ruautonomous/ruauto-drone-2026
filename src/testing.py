import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.logger import log_system
from utils.mission import Mission
from utils.reposition import reposition_drone_deg
from utils.takeoff import takeoff
from utils.geofence import Geofence
import helper.motor_test as motor_test
import helper.servo_test as servo_test 
from helper.file_reader import read_file

from missions.waypointnavigation import WaypointNavigation
from missions.targetlocalization import TargetLocalization

async def main():
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    # await mission_picker(drone)
    #mission = Mission(drone=drone, waypointsFile='info_files/waypoints.txt')
    #fence = Geofence(drone=drone, geofenceFile='info_files/test_files/testingfence.txt')
    # coord = [-35.3628918, 149.1654175, 10]
   
    waypointNav = WaypointNavigation(drone, 'info_files/test_files/test_waypoint_nav.txt')
    targetloc = TargetLocalization(drone)
    
    
    await asyncio.gather(
        drone.start_background_processes(), 
        drone.watch_for_heartbeat(),
        # targetloc.begin_dummy_mission()
        #motor_test.test_all_motors_multiple(drone=drone, num_times=3, throttle_step=5, throttle_value=20)
        # servo_test.full_spin_servo(drone, 1)
        #servo_test.servo_open_close(drone=drone, servo_value=800)
        servo_test.unravel_spool(drone=drone, servo_num=1),
        servo_test.unravel_spool(drone=drone, servo_num=3, opposite=True)
    )

def file_test():
    read_file("info_files/test_files/file_read_test.txt")

async def tmux_test():
    i = 1
    while True:
        print(f"Counter: {i}")
        await asyncio.sleep(1)
        i += 1

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(tmux_test())
    #file_test()
