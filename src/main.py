import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.logger import log_system
from utils.mission import Mission



async def main():
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    mission = Mission(drone=drone)
    
    

    await asyncio.gather(
        drone.start_background_processes(), 
        drone.watch_for_heartbeat(),
        # mission.upload_mission()
        )

if __name__ == "__main__":
    asyncio.run(main())