import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common

connection = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=57600)
connection.wait_heartbeat()

print('connected')