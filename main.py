from drone import Drone
from pymavlink.dialects.v20 import common 
import asyncio
from mission import Mission
from modes import Modes
import file_reader

# waypoints = [[-35.3628918, 149.1654175], 
#              [-35.3624307, 149.1650085], 
#              [-35.3626968, 149.1644055], 
#              [-35.3632437, 149.1645017], 
#              [-35.3635515, 149.1648355]]

            # COORDINATES BELOW ARE LAST YEAR CUASC GEOFENCE BOUNDARY
            # [[35.05932,-118.149], 
            #  [35.06496,-118.156], 
            #  [35.06062,-118.163], 
            #  [35.05932,-118.163]]

# geofence_points= [
#              [35.05932,-118.149], 
#              [35.06496,-118.156], 
#              [35.06062,-118.163], 
#              [35.05932,-118.163]]


config = file_reader.read_config_file()
waypoints = file_reader.read_waypoints()
geofence_points = file_reader.read_geofence()

print(config)
print(waypoints)
print(geofence_points)

drone = Drone()
drone.connect_drone()
from messages import MessageStream 

connection = drone.get_connection()
msg_stream = MessageStream(drone=connection)
drone.set_message_stream(msg_stream)

mission = Mission(drone, waypoints)
modes = Modes(drone)

async def main():
    print('running')
    
    await asyncio.gather(drone.start_processes(msg_stream.stream), mission.upload_mission(), modes.rtl())


asyncio.run(main())



