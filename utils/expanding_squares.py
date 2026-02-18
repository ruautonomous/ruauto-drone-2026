from drone import Drone
from pymavlink.dialects.v20 import common
from mission import Mission
import asyncio

'''
So we can either do this using a mission or just through guided movement

Pros/Cons of Mission:
Pro - Easier to implement
Con - More rigid & hard to change once mission uploaded
Con - Harder to change mid mission

Pros/Cons of Guided Flight:
Pro - More flexible control
Pro - Easier to change the flight's plan 
Con - Not a program that runs once to upload a mission and terminates; has to keep running on event loop until its goal is accomplished


Havily leaning towards Guided Flight tho.

'''

async def expanding_square_search(drone: Drone):
    await drone.get_position()
    
    pass