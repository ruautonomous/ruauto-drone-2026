import asyncio
from drone import Drone
from takeoff import Takeoff
from mission import Mission


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
                await self.takeoff.takeoff_from_current_pos()

            await self.takeoff.modes.set_mode('auto')

        await self.takeoff.modes.rtl()
        pass