from pymavlink import mavutil
from pymavlink.dialects.v20 import common
import asyncio
import file_reader
class Guided:


    def __init__(self, drone: mavutil.mavtcp):
        self.drone = drone
        pass


print(file_reader.read_config_file())

# config = {}
# with open('info_files/config.txt') as f:
#     while True:
#         read = f.readline()
#         if(read == ''):
#             break
#         read = read.removesuffix('\n').split('=')
#         config[read[0]] = read[1]
#         print(f'{read}')
#     print(config)