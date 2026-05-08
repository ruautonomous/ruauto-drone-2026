import asyncio
from ultralytics import YOLO
from pymavlink import mavutil
import cv2
import cv2
from pymavlink.dialects.v20 import common
import math
import numpy as np

from pyparsing import results

from helper.math_funcs import calculate3Ddist, haversine_distance
from ultralytics import YOLO

from utils.drone import Drone, DroneProperties
from utils.takeoff import *
from utils.speed import change_speed
import utils.mode as mode
from utils.armdisarm import *
from utils.reposition import *

from helper.file_controller import *
from helper.gimbal import reposition_gimbal
from helper.file_reader import *

from helper.serve_object_coords import serve_object_coords

'''
• 5-10 objects will be distributed within a predefined area of the competition course.
• A very rough set of bounding GPS coordinates will be provided, and four larger objects will
define a tighter area which contains all identification objects.
• Teams must localize and identify the targets, providing a list of their locations and identifying
number no later than 30 minutes after the end of their flight slot. The UAS must not descent
below 25 feet (7.62 meters) while searching for objects.
• If all objects are correctly identified and localized, a total of 14 points will be awarded.
• 0.5 points will be deduced for each object that is either not correctly identified or not correctly
localized, and 1 point if both are true.
• If the UAS descends below 25 feet but not below 20 feet, 3 points will be deducted from the
calculated score. If the UAS descends below 20 feet, a flat score of 0 will be awarded.
'''

class TargetLocalization:

    # CONSTANTS
    MIN_ALT_METERS = 30/3.281   # 30 feet / 3.281 = X meters
    PIXEL_TOLERANCE = 20     # pixels deadband
    GAIN = 0.002             # velocity scaling factor
    MAX_VEL = 1.0            # m/s cap

    def __init__(self, drone: Drone, initFile: str = None):
        self.drone = drone
        self.file = initFile
        self.newest_frame = None
        self.bounding = read_geofence(initFile)
        pass



    async def upload_mission(self, rtl=True):
        await takeoff(drone=self.drone, target_alt = self.MIN_ALT_METERS) # set takeoff alt to whatever imaging wants
        await reposition_gimbal(drone=self.drone, pitch=-90)
        asyncio.create_task(self.camera())
        await reposition_drone_deg(drone=self.drone, coordinates=self.bounding[0]) # relocating drone to first bounding box point
        if rtl:
            await return_to_launch(drone=self.drone)
        pass

    async def gcp_mission(self, frame):
        model = YOLO("yolov26n.pt")
        results = model.track(source=frame, stream=True)
        ordered_pairs = []
        for r in results:
            if r.boxes.id is not None:
                boxes = r.boxes.xyxy.cpu().numpy()
                track_ids = r.boxes.id.cpu().numpy()
                for box, track_id in zip(boxes, track_ids):
                    drone_position = await self.drone.get_position_deg()  # latitude, longitude, altitude
                    drone_heading = await self.drone.get_heading()
                    coords = serve_object_coords(box, frame.shape, drone_position["lat"], drone_position["long"],
                                                 drone_position["alt"], drone_heading)

                    ordered_pairs.append(coords)
        current_position = await self.drone.get_position_deg()
        closest_node = (np.inf, np.inf)
        arranged_graph = []  # Changed to a list for mutability

        # Make a mutable copy of ordered_pairs if you intend to modify it
        ordered_points_to_process = list(ordered_pairs)

        for j in range(math.factorial(len(ordered_points_to_process))):
            if not ordered_points_to_process:
                break  # No more points to process

            closest_node_current_iteration = None
            min_distance = float('inf')

            for i in ordered_points_to_process:
                print(f"FROM TARGETLOCALIZATION: i = {i}")
                distance_to_i = haversine_distance(i, current_position)
                if distance_to_i < min_distance:
                    min_distance = distance_to_i
                    closest_node_current_iteration = i

            if closest_node_current_iteration is not None:
                arranged_graph.append(closest_node_current_iteration)
                ordered_points_to_process.remove(
                    closest_node_current_iteration)  # Correct way to remove an element from a list
                current_position = closest_node_current_iteration
            else:
                break  # Should not happen if ordered_points_to_process is not empty
        return arranged_graph
    async def camera(self):
        cam_id = 0

        # Initialize capture
        # We try V4L2 first as it's standard for the SIYI A8 Mini
        cap = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)

        # Set the resolution to match your SIYI output
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not cap.isOpened():
            print(f"Error: Could not open camera at /dev/video{cam_id}")
            return

        print("Stream Started. Press 'q' to exit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Empty frame received. Check connections.")
                break
            else:
                self.set_camera_frame(frame)
            await asyncio.sleep(1)

    def set_camera_frame(self, frame):
        self.newest_frame = frame

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

def pixel_to_world(cx, cy, map_width, map_height, world_width, world_height):
        x = (cx / map_width) * world_width
        y = (cy / map_height) * world_height
        return x, y


'''
class Edge:
    def __init__(self, u, v, weight):
        self.u = u
        self.v = v
        self.weight = weight

    def __lt__(self, other):
        return self.weight < other.weight

    def cost_edges(arranged_graph):
        n = len(arranged_graph)
        # I coded cost edges to be dynamic with arranged_graph, change if this is false
        # edges = [ # this will be the graph representation of the gcp squares
        #     Edge(0, 1, 10),
        #     Edge(0, 2, 6),
        #     Edge(0, 3, 5),
        #     Edge(1, 3, 15),
        #     Edge(2, 3, 4)
        # ]
        edges = []

        for i in range(n):
            for j in range(i+1,n):
                w=calculate3Ddist(arranged_graph[i], arranged_graph[j])
                edges.append(Edge(i, j, w))

        cost = 0
        tree_id = [i for i in range(n)]
        result = []

        edges.sort()

        for e in edges:
            if tree_id[e.u] != tree_id[e.v]:
                cost += e.weight
                result.append(e)

                old_id = tree_id[e.u]
                new_id = tree_id[e.v]

                for i in range(n):
                    if tree_id[i] == old_id:
                        tree_id[i] = new_id


        print("Edges in MST:")
        for e in result:
            print(e.u, "-", e.v, ":", e.weight)

        print("Total cost:", cost)
'''