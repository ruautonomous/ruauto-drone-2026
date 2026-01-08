from drone import Drone
import asyncio
import logger
from utils.math_funcs import haversine_distance
from mission import Mission
from takeoff import Takeoff
'''
• Waypoint data will be provided on the day of competition to teams in an unordered list of latitude, longitude, and altitude (in meters) of each waypoint.
• The UAS shall fly a path of its own determination passing each of the waypoints.
• The UAS shall complete the Waypoint Navigation Flight in less than 10 minutes.
• A small data logger provided by the Judges containing a GPS and radio transmitter must be
attached to the UAS for the entirety of the waypoint navigation segment. Details regarding the
size and mass of the logger will be announced in the coming months. Teams are responsible for
ensuring the logger can be securely mounted to the UAS.
'''


# for the sake of simplicity, im only considering latitude and longitude when calculating distances between points 
# i dont think altitude changes enough for it to be significant. will update calculation code if it proves to be worthwhile
class WaypointNav:
    def __init__(self, drone: Drone, points: list):
        self.drone = drone
        self.points = points
        self.takeoff = Takeoff(drone)
        pass
    
    async def begin_setup(self):
        
        self.points = await self.organize_points()
        self.mission = Mission(self.drone, self.points)
        print('Beginning Mission Upload')
        await self.mission.upload_mission()
        print('Mission Uploaded')
        # await self.takeoff.takeoff_from_current_pos()

        pass

    async def organize_points(self) -> list:
        organized_points = []
        current_pos = await self.drone.get_position_deg()
        
        organized_points = self.next_closest_point(current_pos, organized_points)

        logger.log_custom( f'FINAL WAYPOINTS LIST ORDERED: {organized_points}', important=True)
        return organized_points

    def next_closest_point(self, current_pos, organized_points: list):

        if(len(self.points) == 0):
            return organized_points

        dists = [haversine_distance(current_pos, point) for point in self.points]
        # logger.log_custom(f'Drone distances from waypoints: {dists}') # for debugging

        organized_points.append(self.points[dists.index(min(dists))])
        # print(f'Next pos is index: {dists.index(min(dists))}') # for debugging
        current_pos = self.points[dists.index(min(dists))]
        self.points.remove(current_pos)
        # print(f'Organized Points {organized_points}') # for debugging
        
        return self.next_closest_point(current_pos, organized_points)
        
