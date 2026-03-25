import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

from utils.drone import Drone, DroneProperties
import utils.mode as mode
from utils.mission import Mission
from utils.armdisarm import arm_drone

from helper.file_reader import read_waypoints

class CircuitTimeTrial:
    def __init__(self, drone: Drone, waypointsFile: str = None):
        self.drone = drone
        self.custom_points = read_waypoints(waypointsFile) if waypointsFile else None
        self.mission_handler = Mission(waypointsFile=waypointsFile)
        pass

    async def begin_mission(self):
        home_pos = await self.drone.get_home_position_int()
        print(home_pos)
        self.points.append([home_pos['lat'], home_pos['long'], self.drone.target_alt])
        lap = 1
        total_time_elapsed = 0
        self.mission = Mission(self.drone, self.points)
        while True:
            if (lap > 3):
                break
            start_time = time.perf_counter()
            if lap == 1:
                await self.mission.upload_mission(rtl=False, begin_immediately=True)
                await self.drone.send_command(command=common.MAV_CMD_DO_CHANGE_SPEED, param1=common.SPEED_TYPE_AIRSPEED,
                                              param2=self.drone.airspeed, param3=-1)
                takeoff_time = time.perf_counter()
                total_time_elapsed += (takeoff_time - start_time)
                log_system(msgname="TIME ELAPSED SINCE TAKEOFF", msg=f"Time since takeoff: {takeoff_time - start_time}")
            else:
                log_system(msgname=f"LAP {lap}",
                           msg=f"BEGINNING LAP {lap}. {'Let us get a better lap time!!' if lap == 2 else 'One last shot!'}")
                await self.drone.send_command(command=common.MAV_CMD_DO_SET_MISSION_CURRENT, param1=1, param2=1)
            lap_start = time.perf_counter()

            while True:
                reached = await self.drone.message_stream.wait_for_message('MISSION_ITEM_REACHED')
                if (reached.seq == self.mission.mission_length - 1):
                    lap_end = time.perf_counter()
                    log_system(msgname="LAP TIME", msg=f"Time took to complete lap {lap}: {lap_end - lap_start}")
                    total_time_elapsed += (lap_end - lap_start)
                    break

            lap = lap + 1
            log_system(msgname="TOTAL TIME ELAPSED", msg=f"{lap_end - start_time}", color=bcolors.SUCCESS)