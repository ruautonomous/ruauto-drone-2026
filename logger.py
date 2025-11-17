from pymavlink import mavutil

# Purpose: To take in message and print them to console with color
import asyncio

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# print(bcolors.WARNING + "Warning: No active frommets remain. Continue?" + bcolors.ENDC)
# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal

async def logger(stream:asyncio.Queue):
    while True:
        msg = await stream.get()
        print('getting from message-stream')
        log_message(msg)

def log_message(msg):
    if msg.msgname == 'HEARTBEAT' and msg.type == 2:
        print(f'{bcolors.FAIL + msg.msgname + ' (drone) > ' + bcolors.ENDC} {msg}')
        return
    elif msg.msgname == 'HEARTBEAT' and msg.type == 6:
        print(f'{bcolors.FAIL + msg.msgname + ' (gcs)  > ' + bcolors.ENDC} {msg}')
        return
    print(f'{bcolors.WARNING + msg.msgname + bcolors.ENDC} > {msg}')
        
    

