from pymavlink import mavutil
import utils.file_reader as file_reader


config = file_reader.read_config_file()

print(f'Attempting to connect to {config['connection']}')

connection = mavutil.mavlink_connection(config['connection'])
connection.wait_heartbeat()



while(True):
    hb = connection.recv_match(type='HEARTBEAT', blocking=True)
    print(hb)

