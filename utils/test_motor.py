from drone import Drone
from messages import MessageStream
import utils.file_reader as file_reader
from pymavlink.dialects.v20 import common

config = file_reader.read_config_file()
drone = Drone('info_files/params.txt')
drone.connect_drone(config['connection'])

connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)

drone.send_command(command=common.MAV_CMD_DO_MOTOR_TEST, param1=1, param2=common.MOTOR_TEST_THROTTLE_PERCENT,param3 = 5, param5 = 4)


