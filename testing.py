from drone import Drone
from utils.file_reader import read_config_file
from messages import MessageStream
import asyncio
from pymavlink.dialects.v20 import common

config = read_config_file()

drone = Drone('info_files/settings.txt')
drone.connect_drone(config['connection'])

connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)

async def main():

    await asyncio.gather(drone.start_processes(msg_stream.stream), test_servo(drone))
    pass

async def test_servo(drone:Drone):
    await drone.send_command(command=common.MAV_CMD_DO_SET_SERVO, param1=14, param2=1500)
    pass

asyncio.run(main())
