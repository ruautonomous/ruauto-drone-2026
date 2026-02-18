'''

1) Takeoff from compass rose (current pos)

2) Go to bullseye from coordinates we get from imaging

3) Lower the rope from airdrop mechanism (using a servo)

4) dettach the rope (essentially dropping the cube)

5) Return to home (make this a function within this file cuz we may not actually land, rather do a different flight after)

'''
import  asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common
from drone import Drone


class PackageDelivery:
    def __init__(self, drone: Drone):
        self.drone = drone
        pass

    async def begin_mission(self):
        
        pass


