import asyncio
from utils.drone import Drone




async def main():
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    
    await drone.start_background_processes()

if __name__ == "__main__":
    asyncio.run(main())