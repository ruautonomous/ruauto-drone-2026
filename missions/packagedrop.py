from pymavlink.dialects.v20 import common
from logger import log_system
from drone import Drone
import asyncio

'''
The UAS shall drop a package at a well-marked target.
• The package is to be dropped for an altitude of at least 20 feet AGL.
• The package will be provided. It is a beanbag that weighs approximately 130g and is 6.4cm in
diameter. An example may be found on amazon.com
https://www.amazon.com/dp/B07YSYLXR4?ref=ppx_pop_dt_b_product_details&th=1
• The impact of the dropped package will not be measured.
• The time of the flight will be measured and factored into the score.
• The primary scoring metric will be the accuracy of the drop after the package comes to rest.
Meaning, if the package impacts near center but bounces outwards, less points will be awarded.
'''

class PackageDrop:
    def __init__(self, drone: Drone):
        self.drone = drone
        pass

    async def begin_mission():
        pass