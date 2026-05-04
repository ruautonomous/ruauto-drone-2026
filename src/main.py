import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.logger import log_system
from utils.mission import Mission
from utils.reposition import reposition_drone_deg
from utils.takeoff import takeoff
from utils.geofence import Geofence

from helper.file_reader import read_config_file

from missions.waypointnavigation import WaypointNavigation
from missions.circuittimetrial import CircuitTimeTrial
from missions.targetlocalization import TargetLocalization
from missions.packagedrop import PackageDrop
from missions.packagedelivery import PackageDelivery
from missions.packagerecovery import PackageRecovery
from missions.autotests import *

async def main():
    config = read_config_file('info_files/config.txt')
    drone = Drone()
    drone.initialize_drone(parametersFile='info_files/settings.txt', configFile='info_files/config.txt')
    # mission = Mission(drone=drone, waypointsFile='info_files/waypoints.txt')
    fence = Geofence(drone=drone, geofenceFile=config['fenceFile'])
    
    await asyncio.gather(
        drone.start_background_processes(), 
        drone.watch_for_heartbeat(),
        fence.upload_fence(),
        mission_picker(drone)
        )


async def mission_picker(drone: Drone):
    '''Gets the missions needed to be executed via the config.txt file and executes them one after another. Supports multiple missions seperated by commans
    in the config.txt file'''
    config = drone.get_configuration()
    mission_config: str = config['mission']
    missions = []
    while True:
        if mission_config.__contains__(","):
            m = int(mission_config[0:mission_config.index(",")])
            missions.append(m)
            mission_config = mission_config[mission_config.index(",")+1:]
        else:
            missions.append(int(mission_config))
            break
    
    print(f'MISSIONS = {missions}')
    mission_list = {
        0:"NO MISSION",
        1:"WAYPOINT NAVIGATION",
        2:"CIRCUIT TIME TRIAL",
        3:"TARGET LOCALIZATION",
        4:"PACKAGE DROP",
        5:"PACKAGE DELIVERY",
        6:"PACKAGE RECOVERY",
        10: "SIMPLE TAKEOFF LAND",
        11: "GEOFENCE BREACH"
    }

    mission_files = read_config_file('info_files/mission_files.txt')

    while(missions.__len__() != 0):
        current_mission = missions[0]
        print(f"starting mission {mission_list[current_mission]}")
        missions.remove(current_mission)
        read_file = mission_files[f'{current_mission}'] if current_mission < 10 else -1

        mission_rtl = True if missions.__len__() == 0 else False # if the # of missions remaining is zero, then we return to launch
        
        match(current_mission):
            case 0:
                pass
            case 1:
                waypointNav = WaypointNavigation(drone, read_file)
                await waypointNav.upload_mission(rtl = mission_rtl)
            case 2:
                circuitTimeTrial = CircuitTimeTrial(drone, read_file)
                await circuitTimeTrial.upload_mission(rtl = mission_rtl)
            case 3:
                targetLocalization = TargetLocalization(drone, read_file)
                await targetLocalization.upload_mission(rtl = mission_rtl)
                print('target localization')
            case 4:
                packageDrop = PackageDrop(drone, read_file)
                await packageDrop.upload_mission(rtl = mission_rtl)
                print('package drop')
            case 5:
                print('package delivery')
                packageDelivery = PackageDelivery(drone=drone, initFile=read_file)
                await packageDelivery.upload_mission(rtl=mission_rtl)
            case 6:
                print('package recovery')
                packageRecovery = PackageRecovery(drone=drone, initFile = read_file)
                await packageRecovery.upload_mission(rtl=mission_rtl)
            # ALL AUTONOMOUS TESTING FLIGHTS START AT 10. anything below 10 is an official mission
            case 10:
                print('simple takeoff land mission')
                await takeoff_land(drone=drone)
            case 11:
                print("geofence breach")
                await breach_geofence(drone=drone, alt = 5)
                

                

        



if __name__ == "__main__":
    asyncio.run(main())



