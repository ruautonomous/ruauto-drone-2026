from pymavlink import mavutil
from pymavlink.dialects.v20 import common

# important coordinate
# home position: 35.0607124,-118.1558405

# ../Tools/autotest/sim_vehicle.py -v ArduCopter -l 35.0607124,-118.1558405,0,0 --no-rebuild --no-configure


waypoints = [[-35.3628918, 149.1654175], 
             [-35.3624307, 149.1650085], 
             [-35.3626968, 149.1644055], 
             [-35.3632437, 149.1645017], 
             [-35.3635515, 149.1648355]]

geofence_points=[[-35.3620520, 149.1644441], [-35.3618603, 149.1660865], [-35.3636463, 149.1664697], [-35.3638879, 149.1647474]]




connection = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=57600)
connection.wait_heartbeat()

print('connected')


connection.mav.command_long_send(connection.target_system, connection.target_component, common.MAV_CMD_REQUEST_MESSAGE, 0, 
                                 common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,0,0,0,0,0,0)

pos = connection.recv_match(type="GLOBAL_POSITION_INT", blocking=True) # I should've named this home_pos or sm but its fine for now ig
alt = 5 # target altitude

print(pos.lat)
print(pos.lon)
print(pos.relative_alt)

connection.mav.mission_clear_all_send(connection.target_system, connection.target_component, common.MAV_MISSION_TYPE_MISSION)

connection.mav.mission_count_send(connection.target_system,connection.target_component, len(waypoints)+2, common.MAV_MISSION_TYPE_MISSION,0)
print(f"Sending ")


msg = connection.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
print(msg)

print('Sending takeoff command')
connection.mav.mission_item_int_send(connection.target_system,connection.target_component, 0, common.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, common.MAV_CMD_NAV_TAKEOFF,
                                     1,1,0,0,0,0,(int)(pos.lat),(int)(pos.lon), alt, common.MAV_MISSION_TYPE_MISSION)
print("Takeoff sent!")
msg = connection.recv_match(type="MISSION_ACK", blocking=True)
print(msg)
for i,wp in enumerate(waypoints, start=1):
    lat, lon = wp
    
    msg = connection.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
    print(msg)
    
    print(f'Sending lat {lat} and long {lon} as mission item {i}')
    connection.mav.mission_item_int_send(connection.target_system,connection.target_component, i, common.MAV_FRAME_GLOBAL_RELATIVE_ALT, common.MAV_CMD_NAV_WAYPOINT,
                                     0,1,0,0,0,0,(int)(lat*1e7), (int)(lon * 1e7), alt, common.MAV_MISSION_TYPE_MISSION)
    print('Sent!')


msg = connection.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
print(msg)

print('Sending Land Command!')
connection.mav.mission_item_int_send(connection.target_system,connection.target_component, len(waypoints)+1, common.MAV_FRAME_GLOBAL_RELATIVE_ALT, common.MAV_CMD_NAV_LAND,
                                     0,1,0,0,0,0,pos.lat, pos.lon, 0, common.MAV_MISSION_TYPE_MISSION)
print('Land Command Sent!')

msg = connection.recv_match(type="MISSION_ACK", blocking=True)
print(msg)
print('Mission Uploaded!')




connection.mav.command_long_send(connection.target_system, connection.target_component, common.MAV_CMD_COMPONENT_ARM_DISARM, 0, 
                                 1, 0,0,0,0,0,0)

msg = connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)

connection.mav.command_long_send(connection.target_system, connection.target_component, common.MAV_CMD_DO_SET_MODE, 0, 
                                 common.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4,0,0,0,0,0)

msg = connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)

connection.mav.command_long_send(connection.target_system, connection.target_component, common.MAV_CMD_NAV_TAKEOFF, 0, 
                                 0,0,0,0,pos.lat, pos.lon, alt)

msg = connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)

from time import sleep
while 1:
    connection.mav.command_long_send(connection.target_system, connection.target_component, common.MAV_CMD_REQUEST_MESSAGE, 0, 
                                 common.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,0,0,0,0,0,0)
    
    current_pos = connection.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
    current_alt = current_pos.relative_alt / 1000.0
    print(f'Current Alt: {current_alt}')
    if(current_alt > 0.9 * alt and current_alt < 1.1 * alt):
        print(f"Relative Alt: {current_alt} --> Target Alt: {alt}")
        break

    sleep(1) # not tryna see 1000 'current alt' messages in the terminal every second

print('Reached target altitude!')


connection.mav.command_long_send(connection.target_system, connection.target_component, common.MAV_CMD_DO_SET_MODE, 0, 
                                 common.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 3,0,0,0,0,0)

msg = connection.recv_match(type="COMMAND_ACK", blocking=True)
print(msg)


