from pymavlink import mavutil
from pymavlink.dialects.v20 import common
# Purpose: To take in message and print them to console with color
import asyncio

class bcolors:
    # https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m' # bright red
    HEARTBEAT = '\033[31m' # red
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# print(bcolors.WARNING + "Warning: No active frommets remain. Continue?" + bcolors.ENDC)
# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal

async def logger(stream:asyncio.Queue):
    while True:
        msg = await stream.get()
        # print('getting from message-stream')
        log_message(msg)

def log_message(msg):
    if msg.msgname == 'HEARTBEAT' and msg.type == 2:
        print(f'{bcolors.HEARTBEAT + msg.msgname + ' (drone) > ' + bcolors.ENDC} {msg}')
        return
    elif msg.msgname == 'HEARTBEAT' and msg.type == 6:
        # print(f'{bcolors.HEARTBEAT + msg.msgname + ' (gcs)  > ' + bcolors.ENDC} {msg}')
        return
    elif msg.msgname == 'COMMAND_ACK':
        command_log(msg)
    else:
        print(f'{bcolors.WARNING + msg.msgname + bcolors.ENDC} > {msg}')
        
def command_log(msg):
    print_str = (f'{bcolors.OKBLUE + msg.msgname + bcolors.ENDC} ({bcolors.OKCYAN}{msg.command}{bcolors.ENDC}) - ')
    match msg.result:
        case common.MAV_RESULT_ACCEPTED:
            print_str = print_str + f'{bcolors.OKGREEN}{msg.result}{bcolors.ENDC}'
            pass
        case common.MAV_RESULT_DENIED:
            print_str = print_str + f'{bcolors.FAIL}{msg.result}{bcolors.ENDC}'
            pass
        case _:
            print_str = print_str + f'{bcolors.WARNING}{msg.result }{bcolors.ENDC}'
    
    print_str = print_str + f' > {msg}'
    # print(f'{bcolors.OKGREEN + msg.msgname + ' (gcs)  > ' + bcolors.ENDC} {msg}')
    print(print_str)

def mission_log(msg):
    pass

