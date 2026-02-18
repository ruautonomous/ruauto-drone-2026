from drone import Drone
from utils.file_reader import read_config_file
from messages import MessageStream
import asyncio

config = read_config_file()

drone = Drone('info_files/settings.txt')
drone.connect_drone(config['connection'])

connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)

async def main():
    
    await asyncio.gather(drone.start_processes(msg_stream.stream))
    pass

asyncio.run(main())
