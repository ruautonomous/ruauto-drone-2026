import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.logger import log_system
from utils.mission import Mission
from utils.reposition import reposition_drone_deg
from utils.takeoff import takeoff
from utils.geofence import Geofence
import helper.motor_test as motor_test

async def main():
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    
    await asyncio.gather(
        drone.start_background_processes(), 
        drone.watch_for_heartbeat(),
        motor_test.test_all_motors(drone=drone)
        )

if __name__ == "__main__":
    asyncio.run(main())