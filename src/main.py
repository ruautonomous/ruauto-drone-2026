import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.logger import log_system
from utils.mission import Mission
from utils.reposition import reposition_drone_deg
from utils.takeoff import takeoff
from utils.geofence import Geofence

async def main():
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    mission = Mission(drone=drone, waypointsFile='info_files/waypoints.txt')
    fence = Geofence(drone=drone, geofenceFile='info_files/testingfence.txt')
    # coord = [-35.3628918, 149.1654175, 10]
    

    await asyncio.gather(
        drone.start_background_processes(), 
        drone.watch_for_heartbeat(),
        fence.upload_fence(),
        mission.upload_mission(begin_immediately=True)
        # takeoff(drone=drone)
        # reposition_drone_deg(drone, coord)
        )

if __name__ == "__main__":
    asyncio.run(main())