import asyncio
from ultralytics import YOLO
from pymavlink import mavutil
import cv2
import cv2
from pymavlink.dialects.v20 import common
import math
import numpy as np
import itertools
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
    # Latitude meters-per-degree approximation coefficients (all in meters).
    LAT_METERS_COEFF_A = 111132.92
    LAT_METERS_COEFF_B = 559.82
    LAT_METERS_COEFF_C = 1.175
    # ~0.11 m in latitude degrees, enough to avoid duplicate lane endpoints from float drift.
    LANE_LAT_TOLERANCE_DEG = 1e-6
    LANE_LONG_TOLERANCE_DEG = 1e-6

    def __init__(self, drone: Drone, initFile: str = None):
        self.drone = drone
        self.file = initFile
        self.newest_frame = None
        self.bounding = read_geofence(initFile)
        self.num_targets = 10
        self.gcp_squares = []
        self.unvisited_gcps = []
        pass



    async def upload_mission(self, rtl=True):
        await takeoff(drone=self.drone, target_alt = self.MIN_ALT_METERS) # set takeoff alt to whatever imaging wants
        await reposition_gimbal(drone=self.drone, pitch=-90)
        asyncio.create_task(self.camera())
        # await reposition_drone_deg(drone=self.drone, coordinates=self.bounding[0]) # relocating drone to first bounding box point
        await self.lawnmower_search()
        #gcp_mission(frame=self.newest_frame)
        while len(self.gcp_squares) < self.num_targets:
            potentital_gcp = await self.gcp_mission(self.newest_frame)


        if rtl:
            await return_to_launch(drone=self.drone)
        pass
    def update_s
    async def gcp_mission(self, frame):
        model = YOLO("best.onnx")
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
        #current_position = await self.drone.get_position_deg()
        return ordered_pairs
    def compute_optimal_route(self, current_pos, unvisited_gcps):
        #code TSP(calculate haversine distance for all of the points
        shortest_path_cost = float('inf')
        best_next_node = None
        for path in itertools.permutations(unvisited_gcps):
            total_distance = 0
            current_node = current_pos
            for point in path:
                total_distance+=haversine_distance(point, current_node)
                current_node = point
            if total_distance < shortest_path_cost:
                shortest_path_cost = total_distance
                best_next_node = path[0]
        return best_next_node
    async def lawnmower_search(self, lane_spacing_meters: float = 5):
        """
        Fly a lawnmower sweep inside the provided geofence polygon.
        Assumes geofence points form a convex polygon (e.g., 4-point bounding area).
        Lanes are generated from min/max latitude and then clipped per-lane to
        polygon edge intersections, so each traversed segment stays within the
        given coordinates. If insufficient geofence points are provided, the
        search is skipped.
        """
        if lane_spacing_meters <= 0:
            raise ValueError("lane_spacing_meters must be greater than 0.")

        if self.bounding is None or len(self.bounding) < 3:
            print("Lawnmower search skipped: insufficient geofence points.")
            return

        polygon_points = self._get_ordered_polygon_points(self.bounding)
        lats = [point[0] for point in polygon_points]

        min_lat = min(lats)
        max_lat = max(lats)

        center_lat_rad = math.radians((min_lat + max_lat) / 2.0)
        meters_per_degree_lat = (
            self.LAT_METERS_COEFF_A
            - self.LAT_METERS_COEFF_B * math.cos(2 * center_lat_rad)
            + self.LAT_METERS_COEFF_C * math.cos(4 * center_lat_rad)
        )

        lane_spacing_deg_lat = lane_spacing_meters / meters_per_degree_lat

        current_pos = await self.drone.get_position_deg()
        search_alt = max(current_pos["alt"], self.MIN_ALT_METERS)

        lane_lats = [min_lat]
        lane_lat = min_lat + lane_spacing_deg_lat
        while lane_lat < max_lat - self.LANE_LAT_TOLERANCE_DEG:
            lane_lats.append(lane_lat)
            lane_lat += lane_spacing_deg_lat
        if abs(lane_lats[-1] - max_lat) > self.LANE_LAT_TOLERANCE_DEG:
            lane_lats.append(max_lat)

        for lane_idx, lat in enumerate(lane_lats):
            lane_bounds = self._get_lane_longitude_bounds(lat, polygon_points)
            if lane_bounds is None:
                continue

            min_long, max_long = lane_bounds
            if lane_idx % 2 == 0:
                start_long = min_long
                end_long = max_long
            else:
                start_long = max_long
                end_long = min_long

            await reposition_drone_deg(drone=self.drone, coordinates=[lat, start_long, search_alt])
            await reposition_drone_deg(drone=self.drone, coordinates=[lat, end_long, search_alt])

    def _get_ordered_polygon_points(self, points):
        center_lat = sum(point[0] for point in points) / len(points)
        center_long = sum(point[1] for point in points) / len(points)
        return sorted(
            points,
            key=lambda point: math.atan2(point[0] - center_lat, point[1] - center_long)
        )

    def _get_lane_longitude_bounds(self, lane_lat: float, polygon_points):
        intersections = []
        lat_tol = self.LANE_LAT_TOLERANCE_DEG
        long_tol = self.LANE_LONG_TOLERANCE_DEG
        size = len(polygon_points)

        for idx in range(size):
            lat_1, long_1 = polygon_points[idx]
            lat_2, long_2 = polygon_points[(idx + 1) % size]

            if abs(lat_2 - lat_1) <= lat_tol:
                if abs(lane_lat - lat_1) <= lat_tol:
                    min_long = min(long_1, long_2)
                    max_long = max(long_1, long_2)
                    intersections.extend([min_long, max_long])
                continue

            lower_lat = min(lat_1, lat_2) - lat_tol
            upper_lat = max(lat_1, lat_2) + lat_tol
            if lane_lat < lower_lat or lane_lat > upper_lat:
                continue

            t = (lane_lat - lat_1) / (lat_2 - lat_1)
            intersection_long = long_1 + t * (long_2 - long_1)
            intersections.append(intersection_long)

        if len(intersections) < 2:
            return None

        intersections.sort()
        unique_intersections = [intersections[0]]
        for candidate in intersections[1:]:
            if abs(candidate - unique_intersections[-1]) > long_tol:
                unique_intersections.append(candidate)

        if len(unique_intersections) < 2:
            return None

        return [unique_intersections[0], unique_intersections[-1]]

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