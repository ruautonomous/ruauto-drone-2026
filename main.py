from pymavlink import mavutil
from pymavlink.dialects.v20 import common

connection = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=57600)
connection.wait_heartbeat()

print('connected')


connection.mav.command_long_send(connection.target_system, connection.target_component, common.MAV_CMD_REQUEST_MESSAGE, 0, 
                                 common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,0,0,0,0,0,0)

msg = connection.recv_match(type="GLOBAL_POSITION_INT", blocking=True)


print(msg.lat)
print(msg.lon)
print(msg.relative_alt)

connection.mav.mission_clear_all_send(connection.target_system, connection.target_component, common.MAV_MISSION_TYPE_MISSION)

connection.mav.mission_count_send(connection.target_system,connection.target_component, 100, common.MAV_MISSION_TYPE_MISSION)

msg = connection.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
print(msg)