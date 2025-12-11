from pymavlink import mavutil
from pymavlink.dialects.v20 import common

class Mission:

    async def upload_mission_to_drone():
        pass

    
    #initialize
    def prepareMission(self, connection: mavutil.mavtcp, waypoints):
        connection.mav.mission_clear_all_send(connection.target_system, connection.target_component, common.MAV_MISSION_TYPE_MISSION)
        print("Cleared missions")
        connection.mav.mission_count_send(connection.target_system, connection.target_component, len(waypoints)+2, common.MAV_MISSION_TYPE_MISSION,0)
        print(f"Sending Mission Count")



    #sending waypoints
    def missionSteps(self, connection: mavutil.mavtcp, waypoints, alt: int):
        msg = connection.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
        print("Ready for Mission Upload")

        self.getPosition(connection)
        print('Sending takeoff command')
        connection.mav.mission_item_int_send(connection.target_system, connection.target_component, 0, common.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, common.MAV_CMD_NAV_TAKEOFF,
                                     1,1,0,0,0,0,(int)(self.homePos.lat),(int)(self.homePos.lon), alt, common.MAV_MISSION_TYPE_MISSION)
        print("Takeoff sent!")
        print("\n")

        for i, wp in enumerate(waypoints, start=1):
            lat, lon = wp
            
            msg = connection.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
            print(msg)
            
            print(f'Sending lat {lat} and long {lon} as mission item {i}')
            connection.mav.mission_item_int_send(connection.target_system, connection.target_component, i, common.MAV_FRAME_GLOBAL_RELATIVE_ALT, common.MAV_CMD_NAV_WAYPOINT,
                                            0,1,0,0,0,0,(int)(lat*1e7), (int)(lon * 1e7), alt, common.MAV_MISSION_TYPE_MISSION)
            print('Sent!')
            print("\n")

        msg = connection.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
        print(msg)


        print('Sending Land Command!')
        connection.mav.mission_item_int_send(connection.target_system, connection.target_component, len(waypoints)+1, common.MAV_FRAME_GLOBAL_RELATIVE_ALT, common.MAV_CMD_NAV_LAND,
                                            0,1,0,0,0,0,self.homePos.lat, self.homePos.lon, 0, common.MAV_MISSION_TYPE_MISSION)
        print('Land Command Sent!')

        msg = connection.recv_match(type="MISSION_ACK", blocking=True)
        print("\n")
        print(msg)
        print("\n")

        print('Mission Uploaded!')




#testbed
waypoints = [[-35.3628918, 149.1654175], 
             [-35.3624307, 149.1650085], 
             [-35.3626968, 149.1644055], 
             [-35.3632437, 149.1645017], 
             [-35.3635515, 149.1648355]]

connection = mavutil.mavlink_connection('tcp:127.0.0.1:5763', baud=57600)
connection.wait_heartbeat()

print('connected')
print("\n\n\n")

m1 = Mission()
m1.prepareMission(connection, waypoints)
print("\n\n\n")
m1.missionSteps(connection, waypoints, 20)


