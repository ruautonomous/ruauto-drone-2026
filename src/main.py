import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.logger import log_system



async def main():
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    
    # await asyncio.create_task(drone.start_background_processes())
    
    # await asyncio.create_task(drone.send_command(command=common.MAV_CMD_DO_SET_SERVO, param1=14, param2=1500))

    await asyncio.gather(
        drone.start_background_processes(), 
        drone.watch_for_heartbeat()
        )

if __name__ == "__main__":
    asyncio.run(main())