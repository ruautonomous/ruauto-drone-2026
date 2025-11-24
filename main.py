from drone import Drone
from pymavlink.dialects.v20 import common 
import asyncio

waypoints = [[35.05932,-118.149], 
             [35.06496,-118.156], 
             [35.06062,-118.163], 
             [35.05932,-118.163]]

geofence_points= [[35.05932,-118.149], 
             [35.06496,-118.156], 
             [35.06062,-118.163], 
             [35.05932,-118.163]]
# print('hello world')

drone = Drone()
# print('hello world 2')
drone.connect_drone()
# print('hello world 3')
from messages import MessageStream 

connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)

async def main():
    print('running')
    await asyncio.gather(msg_stream.message_stream(), drone.start_processes(msg_stream.stream))

    

asyncio.run(main())



