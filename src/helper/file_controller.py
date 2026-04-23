import asyncio
from pymavlink.dialects.v20 import common

from utils.drone import Drone
from utils.takeoff import *
from utils.armdisarm import *
from utils.logger import log_system
from utils.reposition import *

'''TRIAL PHASES. NOT GUARANTEED TO BE USED FOR FINAL PRODUCT. MIGHT SCRAP THIS'''
async def execute_file(file, drone: Drone):
    items = []
    with open(file) as f:
        while True:
            read = f.readline()
            if(read == ''):
                print(f'finished reading {items}')
                return items
            if(read.__contains__('#')):
                continue
            read = read.removesuffix('\n')
            
            #FILE REDIRECT
            if read.__len__() >= 7 and read[0:7] == "redir->":
                print(f'redirection encountered. file name: {read[7:]}')

            # REPOSITION
            if read.__len__() >= 6 and read[0:6] == "repo->":
                target_repo = []
                read = read[6:]
                while True:
                    if not read.__contains__(","):
                        target_repo.append(float(read))
                        break
                    target_repo.append(float(read[0:read.index(',')]))
                    read = read[read.index(",")+1:]
                print(f'reposition drone to {target_repo}')
                await reposition_drone_deg(drone=drone, coordinates = target_repo)

            if read.__len__() >= 11 and read[0:11] == "altchange->":
                read = read[11:]
                alt_delta = int(read)
                print(f'changing altitude by {alt_delta} meters')
                await change_altitude(drone=drone, alt_change = alt_delta)
            
            if read.__len__() >= 9 and read[0:9] == "takeoff->":
                read = read[9:]
                takeoff_alt = int(read)
                print('takeoff commencing')
                await takeoff(drone=drone, target_alt = takeoff_alt)
                
            if read.__len__() >= 6 and read[0:6] == "land":
                read = read[6:]
                print('landing read')
                if read == "home":
                    await return_to_launch(drone)
                elif read == "here":
                    print('land here')
            
    return items
            
'''Need to create some sort of scripting/redirection system. if a mission file had to read another file for info, i need to 
    write a standard that can do that. Thinking, if( read == 'redir->[file]): then read [file] recursively etc
    read = "redir->[file name]"
    print(read[0:7]) prints redir->
    print(read[7:]) prints [file name]
    
    redir-> will redirect attention to given file. it will read the commands of the file passed and execute it before returning to current file
    repo-> will reposition the drone given lat,long,alt coordinates. format: repo->[lat],[long],[rel_alt(meters)]
    altchange->[desired relative altitude] - will instruct drone to change its altitude
    takeoff->[takeoff height in meters]
    land->home or land->here - 'home' will tell drone to land at where it left from. 'here' says to land right where it is
    speed->[new speed] - instructs drone to change speed to [new speed]
    mode->[mode name] - instructs drone to change mode
    req->[message name] - requests a message
    sendcmd->[command id]
    '''