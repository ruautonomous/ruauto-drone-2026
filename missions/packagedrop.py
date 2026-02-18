from pymavlink.dialects.v20 import common

from takeoff import Takeoff
from logger import log_system
from takeoff import Takeoff
from mission import Mission
from drone import Drone
import utils.file_reader as file_reader
import asyncio

'''
The UAS shall drop a package at a well-marked target.
• The package is to be dropped for an altitude of at least 20 feet AGL.
• The package will be provided. It is a beanbag that weighs approximately 130g and is 6.4cm in
diameter. An example may be found on amazon.com
https://www.amazon.com/dp/B07YSYLXR4?ref=ppx_pop_dt_b_product_details&th=1
• The impact of the dropped package will not be measured.
• The time of the flight will be measured and factored into the score.
• The primary scoring metric will be the accuracy of the drop after the package comes to rest.
Meaning, if the package impacts near center but bounces outwards, less points will be awarded.
'''


class PackageDrop:
    def __init__(self, drone: Drone, points:list):
        self.drone = drone
        self.points=points
        self.takeoff=Takeoff(drone)
        pass

    async def begin_mission(self, servo_num):
        home_pos = await self.drone.get_home_position()
        print(home_pos)
        self.points.append([home_pos['lat'], home_pos['long'], self.drone.target_alt])
        self.mission = Mission(self.drone, self.points)
        await self.mission.upload_mission(no_rtl=True, takeoff=True)
        await self.takeoff.takeoff_from_current_pos()
        await self.takeoff.modes.set_mode('auto')
        await self.drone.send_command(command=common.MAV_CMD_DO_CHANGE_SPEED, param1=common.SPEED_TYPE_AIRSPEED,
                                      param2=self.drone.airspeed, param3=-1)
        some_number_i_dont_know=10
        servo_num=1
        while True:
            current_pos = await self.drone.get_position_deg()
            if(current_pos<some_number_i_dont_know):
                #After some distance away from the payload drop, the drone should slow down to stablize
                await self.drone.send_command(command=common.MAV_CMD_DO_CHANGE_SPEED, param1=common.SPEED_TYPE_AIRSPEED,
                                          param2=self.drone.airspeed, param3=-1)
                reached = await self.drone.message_stream.wait_for_message('MISSION_ITEM_REACHED')
                if(reached.seq == self.mission.mission_length-1):
                    log_system(msgname='REACHED DROP', msg=f'Ready to drop payload')
                    break
        await self.drone.send_command(command=common.MAV_CMD_DO_SET_SERVO,param1=servo_num,param2=600)
        await self.takeoff.modes.rtl()
        await self.takeoff.reset_drone()

