import asyncio
from drone import Drone
from takeoff import Takeoff
from mission import Mission
from pymavlink.dialects.v20 import common
import time
from logger import log_system, bcolors

'''
Within the region defined by the flight boundaries, there will be as many as 7 circuit waypoints defined.
• Circuit waypoints will be provided on the day of competition to teams in an ordered list of
latitude, longitude, and altitude (in meters) of each circuit waypoint.
• The UAS shall fly a path between the waypoints in order.
• The UAS shall be allowed a maximum of three full circuits to set a time.
• The UAS shall pass within 2 meters of each waypoint, as determined by the Judge-provided data
logger, or the timing for that lap will be invalidated.
• The fastest of the valid laps will be used for final scoring
'''

class CircuitTimeTrial:
    def __init__(self, drone: Drone, points: list):
        self.drone = drone
        self.points = points
        self.takeoff = Takeoff(drone)
        pass


    async def begin_mission(self):
        self.mission = Mission(self.drone, self.points)
        lap = 1
        while True:

            if(lap > 3):
                break

            await self.mission.upload_mission(no_rtl=True)
            if lap == 1:
                start_time = time.perf_counter()
                await self.takeoff.takeoff_from_current_pos()
                await self.takeoff.modes.set_mode('auto')
                await self.drone.send_command(command=common.MAV_CMD_DO_CHANGE_SPEED, param1=common.SPEED_TYPE_AIRSPEED, param2=self.drone.airspeed, param3 = -1)
                takeoff_time = time.perf_counter()
                log_system(msgname="TIME ELAPSED SINCE TAKEOFF", msg=f"Time since takeoff: {takeoff_time-start_time}")
                
            lap_start = time.perf_counter()
            
            while True:
                reached = await self.drone.message_stream.wait_for_message('MISSION_ITEM_REACHED')
                if(reached.seq == self.mission.mission_length-1):
                    lap_end = time.perf_counter()
                    log_system(msgname="LAP TIME", msg=f"Time took to complete lap {lap}: {lap_end-lap_start}")
                    break
            
            lap = lap+1
            log_system(msgname="TOTAL TIME ELAPSED", msg=f"{lap_end-start_time}", color=bcolors.SUCCESS)
        await self.takeoff.modes.rtl()
        pass