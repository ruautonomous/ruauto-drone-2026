import asyncio
from ultralytics import YOLO
from pymavlink import mavutil
import cv2
from pymavlink.dialects.v20 import common

from utils.drone import Drone, DroneProperties
from utils.takeoff import *
from utils.speed import change_speed
import utils.mode as mode
from utils.armdisarm import *
from utils.reposition import *

from helper.file_controller import *



class TargetLocalization:

    # CONSTANTS
    MIN_ALT_METERS = 15   # 30 feet
    PIXEL_TOLERANCE = 20     # pixels deadband
    GAIN = 0.002             # velocity scaling factor
    MAX_VEL = 1.0            # m/s cap

    def __init__(self, drone: Drone, initFile: str = None):
        self.drone = drone
        self.file = initFile
        pass

    def load_model():
        # Load trained YOLO model
        model = YOLO("checkered_detector.pt")   # your trained weights

        # Load map image
        image_path = "map.png"
        image = cv2.imread(image_path)

        # Run detection
        results = model(image)

        locations = []

        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy()

            for box, cls in zip(boxes, classes):
                x1, y1, x2, y2 = box

                # center location of detected square
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                locations.append((cx, cy))

                # draw bounding box
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
                cv2.circle(image, (cx,cy), 4, (0,0,255), -1)

                print(f"Checkered square at: ({cx}, {cy})")

        # Show result
        cv2.imshow("Detections", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print("All square locations:", locations)

    
    def pixel_to_world(cx, cy, map_width, map_height, world_width, world_height):
        '''Unused? I don't know what this is for'''
        x = (cx / map_width) * world_width
        y = (cy / map_height) * world_height
        return x, y



    async def upload_mission(self, rtl=True):
        await execute_file(file=self.file, drone=self.drone)
        pass
        

    async def begin_dummy_mission(self):
        await arm_drone(self.drone)
        await mode.set_mode(drone=self.drone, mode=mode.GUIDED)
        await takeoff(drone=self.drone, target_alt=10)
        await reposition_drone_deg(self.drone, [-35.3618419,149.1651785,10])
        await change_speed(self.drone, 15)

    async def center_on_target(self, target_x, target_y, frame_width, frame_height):

        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2

        error_x = target_x - frame_center_x
        error_y = target_y - frame_center_y

        print("Error X:", error_x, "Error Y:", error_y)

        # Deadband (prevents oscillation)
        if abs(error_x) < self.PIXEL_TOLERANCE:
            error_x = 0
        if abs(error_y) < self.PIXEL_TOLERANCE:
            error_y = 0

        # Convert to velocity
        vx = -error_y * self.GAIN   # forward/back
        vy = -error_x * self.GAIN   # left/right
        vz = 0                 # hold altitude

        # Clamp velocity
        vx = max(min(vx, self.MAX_VEL), -1*self.MAX_VEL)
        vy = max(min(vy, self.MAX_VEL), -1*self.MAX_VEL)

        # Enforce minimum altitude
        current_alt = await self.drone.get_altitude()
        if current_alt < self.MIN_ALT_METERS:
            vz = -0.5  # ascend slightly
        else:
            vz = 0

        reposition_velocity(self.drone, vx=vx, vy=vy, vz=vz)
