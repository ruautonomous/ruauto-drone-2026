import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.logger import log_system
from utils.mission import Mission
from utils.reposition import reposition_drone_deg
from utils.takeoff import takeoff

async def main():
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    mission = Mission(drone=drone)
    
    coord = [-35.3628918, 149.1654175, 10]
    

    await asyncio.gather(
        drone.start_background_processes(), 
        drone.watch_for_heartbeat(),
        # mission.upload_mission()
        takeoff(drone=drone)
        # reposition_drone_deg(drone, coord)
        )

if __name__ == "__main__":
    asyncio.run(main())