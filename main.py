from drone import Drone
from pymavlink.dialects.v20 import common 
import asyncio

drone = Drone()
drone.connect_drone()

from messages import MessageStream 

connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)
async def main():
    await asyncio.gather(msg_stream.message_stream(), drone.set_home_position(), drone.start_processes(msg_stream.stream))

    

asyncio.run(main())



