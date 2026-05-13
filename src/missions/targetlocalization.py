import asyncio
import itertools
import math

import cv2
from ultralytics import YOLO
from ultralytics.solutions import ObjectCropper

from helper.file_reader import read_geofence
from helper.gimbal import reposition_gimbal
from helper.math_funcs import haversine_distance
from helper.serve_object_coords import serve_object_coords
from utils.armdisarm import *
from utils.drone import Drone
from utils.reposition import *
from utils.takeoff import *
from helper.TensorRTClassifer import TensorRTModel, preprocess_image
import numpy as np
'''
• 5-10 objects will be distributed within a predefined area of the competition course.
• A very rough set of bounding GPS coordinates will be provided, and four larger objects will
  define a tighter area which contains all identification objects.
• Teams must localize and identify the targets, providing a list of their locations and identifying
  number no later than 30 minutes after the end of their flight slot. The UAS must not descend
  below 25 feet (7.62 meters) while searching for objects.
• If all objects are correctly identified and localized, a total of 14 points will be awarded.
• 0.5 points will be deducted for each object that is either not correctly identified or not
  correctly localized, and 1 point if both are true.
• If the UAS descends below 25 feet but not below 20 feet, 3 points will be deducted from the
  calculated score. If the UAS descends below 20 feet, a flat score of 0 will be awarded.
'''


class TargetLocalization:

    # --- Flight constants ---
    MIN_ALT_METERS  = 30 / 3.281    # 30 ft → metres (~9.14 m)
    PIXEL_TOLERANCE = 20            # px deadband for center_on_target
    GAIN            = 0.002         # velocity scaling factor
    MAX_VEL         = 1.0           # m/s cap for velocity commands

    # --- Latitude metres-per-degree approximation coefficients ---
    LAT_METERS_COEFF_A = 111132.92
    LAT_METERS_COEFF_B = 559.82
    LAT_METERS_COEFF_C = 1.175

    # --- Lawnmower geometry tolerances ---
    LANE_LAT_TOLERANCE_DEG  = 1e-6
    LANE_LONG_TOLERANCE_DEG = 1e-6

    # --- Detection / deduplication / routing ---
    GCP_DEDUP_MIN_DIST_M = 1.0    # closer than this → same object (metres)
    DETECTION_INTERVAL_S = 0.5    # how often YOLO runs throughout the mission
    CAMERA_INTERVAL_S    = 0.033  # camera capture cadence (~30 fps)

    # After all known targets are visited, wait this long for new detections
    # before declaring the mission complete.
    NEW_TARGET_WAIT_S = 5.0

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #
    def __init__(self, drone: Drone, initFile: str = None):
        self.drone    = drone
        self.file     = initFile

        self.newest_frame = None
        self.bounding     = read_geofence(initFile)
        self.num_targets  = 10

        # All confirmed unique detections: list of (lat, lon, 0) tuples.
        self.gcp_squares: list[tuple] = []

        # Targets already physically visited during the TSP phase.
        # Stored as a set for O(1) membership tests.
        self.visited_gcps: set[tuple] = set()

        # YOLO model loaded ONCE at construction — never reloaded per frame.
        self.model = YOLO("best.onnx")

        self.classifer = TensorRTModel("classifer.engine")
        self.final_gcp_location = []
        # Signals the continuous detection task to exit cleanly.
        self._mission_done = asyncio.Event()

    # ================================================================== #
    #  PUBLIC ENTRY POINT                                                  #
    # ================================================================== #
    async def upload_mission(self, rtl: bool = True):
        """
        Full autonomous mission:

          1. Takeoff + gimbal down.
          2. Start a single detection task that runs for the ENTIRE mission.
          3. Phase 1 — lawnmower sweep; detection populates gcp_squares.
          4. Phase 2 — dynamic TSP visit; route is recomputed after each
             arrival so targets discovered mid-route are never skipped.
          5. Signal detection to stop, then RTL.
        """
        await takeoff(drone=self.drone, target_alt=self.MIN_ALT_METERS)
        await reposition_gimbal(drone=self.drone, pitch=-90)

        # Camera stream — persistent background task for the whole mission.
        asyncio.create_task(self.camera())

        # Detection — runs from takeoff until _mission_done is set.
        # Critically, it is NOT cancelled after the lawnmower; it continues
        # through every TSP waypoint so mid-route discoveries are captured.
        detection_task = asyncio.create_task(self._continuous_detection())

        # ── Phase 1: lawnmower ──────────────────────────────────────────
        print("[Mission] Phase 1: lawnmower search.")
        await self.lawnmower_search()
        print(f"[Mission] Lawnmower complete — "
              f"{len(self.gcp_squares)} unique target(s) found so far.")

        # ── Phase 2: dynamic TSP ────────────────────────────────────────
        # Detection is still running here. New GCPs discovered while
        # flying between waypoints are included in the next route decision.
        print("[Mission] Phase 2: dynamic TSP visit.")
        if self.gcp_squares:
            await self._visit_targets_dynamic_tsp()
        else:
            print("[Mission] No targets detected — skipping TSP phase.")

        # Clean shutdown of the detection task.
        self._mission_done.set()
        await detection_task

        print(f"[Mission] Done — "
              f"{len(self.visited_gcps)}/{len(self.gcp_squares)} target(s) visited.")

        if rtl:
            await return_to_launch(drone=self.drone)

    # ================================================================== #
    #  CONTINUOUS DETECTION  (whole-mission background task)               #
    # ================================================================== #
    async def _continuous_detection(self):
        """
        Runs from takeoff until _mission_done is set.
        Every DETECTION_INTERVAL_S seconds it grabs the latest frame, runs
        YOLO, and merges unique detections into self.gcp_squares.
        This covers both the lawnmower AND all TSP transit legs.
        """
        while not self._mission_done.is_set():
            if self.newest_frame is not None:
                detections = await self._detect_objects()
                added = self._merge_detections(detections)
                if added:
                    print(f"[Detection] +{added} new target(s) → "
                          f"{len(self.gcp_squares)} total unique target(s).")
            await asyncio.sleep(self.DETECTION_INTERVAL_S)

    # ================================================================== #
    #  PHASE 2 — DYNAMIC TSP VISIT                                         #
    # ================================================================== #
    async def _visit_targets_dynamic_tsp(self):
        """
        Visit every target in gcp_squares using a rolling nearest-neighbour
        strategy that re-evaluates the remaining route after EACH arrival.

        Why per-stop re-evaluation instead of a pre-computed fixed route:
          • Detection is still running — new targets may be added to
            gcp_squares at any moment while flying between stops.
          • Re-evaluating after each arrival means any target discovered
            mid-transit is folded into the next leg automatically.

        Termination rules (first satisfied wins):
          1. All num_targets confirmed targets have been visited.
          2. All currently known targets have been visited AND no new
             target appears within NEW_TARGET_WAIT_S seconds.
        """
        while True:

            # ── Build the current unvisited list ─────────────────────────
            unvisited = [g for g in self.gcp_squares
                         if g not in self.visited_gcps]

            # ── Early-exit: all expected targets collected ────────────────
            if len(self.visited_gcps) >= self.num_targets:
                print("[TSP] All expected targets visited. Done.")
                break

            # ── No unvisited targets at this moment ───────────────────────
            if not unvisited:
                print(f"[TSP] No unvisited targets. "
                      f"Waiting {self.NEW_TARGET_WAIT_S}s for new detections…")
                await asyncio.sleep(self.NEW_TARGET_WAIT_S)

                unvisited = [g for g in self.gcp_squares
                             if g not in self.visited_gcps]
                if not unvisited:
                    print("[TSP] No new targets found. Ending TSP phase.")
                    break
                # New targets appeared — fall through and visit them.

            # ── Pick the best next waypoint ───────────────────────────────
            # For ≤ 8 unvisited targets: brute-force the sub-tour and take
            # its first element (optimal immediate next hop).
            # For > 8: take the nearest unvisited target (greedy O(n)).
            # We only commit to ONE hop and recompute after arrival, so
            # newly discovered targets are never bypassed.
            current_pos = await self.drone.get_position_deg()
            next_target = self._pick_next_target(current_pos, unvisited)

            print(f"[TSP] → lat={next_target[0]:.7f}, lon={next_target[1]:.7f} "
                  f"({len(unvisited)} unvisited, "
                  f"{len(self.gcp_squares)} known total).")

            # Fly to the chosen waypoint.
            # Detection continues running during this await, so gcp_squares
            # may grow before we arrive and re-evaluate.
            await reposition_drone_deg(
                drone=self.drone, coordinates=list(next_target))
            classified_objects =await self.classifier()

            our_gcp_squares = classified_objects[0]
            self.final_gcp_location.append(our_gcp_squares)

            # Mark visited only after arrival.
            self.visited_gcps.add(next_target)
            remaining = len(self.gcp_squares) - len(self.visited_gcps)
            print(f"[TSP] Arrived. {len(self.visited_gcps)} visited, "
                  f"{remaining} remaining.")

    # ================================================================== #
    #  NEXT-TARGET SELECTION                                               #
    # ================================================================== #
    def _pick_next_target(self, current_pos: dict,
                          unvisited: list[tuple]) -> tuple:
        """
        Choose the single best immediate next waypoint from unvisited.

        ≤ 8 targets  →  brute-force full sub-tour; return first element.
        > 8 targets  →  nearest-neighbour greedy pick.

        Only the first element is used because the route is recomputed
        after every arrival.
        """
        if not unvisited:
            raise ValueError("_pick_next_target called with empty list.")

        start = (current_pos["lat"], current_pos["long"], 0)

        if len(unvisited) <= 8:
            return self._tsp_brute_force(start, unvisited)[0]

        return min(unvisited, key=lambda t: haversine_distance(start, t))

    # ================================================================== #
    #  OBJECT DETECTION  (single frame pass)                               #
    # ================================================================== #
    async def _detect_objects(self) -> list[tuple]:
        """
        Run YOLO tracking on the latest camera frame.
        Fetches live drone position + heading each call for accurate
        geo-referencing regardless of how fast the drone is moving.

        Returns a list of (lat, lon, 0) tuples.
        """
        frame = self.newest_frame
        if frame is None:
            return []

        drone_pos     = await self.drone.get_position_deg()   # {"lat", "long", "alt"}
        drone_heading = await self.drone.get_heading()        # degrees 0-359

        detections: list[tuple] = []
        results = self.model.track(source=frame, stream=True, persist=True)

        for r in results:
            if r.boxes.id is None:
                continue
            boxes= r.boxes.xyxy.cpu().numpy()
            track_ids = r.boxes.id.cpu().numpy()
            for box, _track_id in zip(boxes, track_ids):
                lat, lon = serve_object_coords(
                    box, frame.shape,
                    drone_pos["lat"], drone_pos["long"],
                    drone_pos["alt"], drone_heading
                )
                detections.append((lat, lon, 0))

        return detections

    async def classifier(self):
        frame = self.newest_frame
        drone_pos = await self.drone.get_position_deg()  # {"lat", "long", "alt"}
        drone_heading = await self.drone.get_heading()
        results = self.model.track(frame, stream=True, persist=True)
        classified_objects = []
        for r in results:
            if r.boxes.id is None:
                continue
            boxes = r.boxes.xyxy.cpu().numpy()
            track_ids = r.boxes.id.cpu().numpy()
            confidence = r.boxes.conf.cpu().numpy()
            for box, _track_ids, conf in zip(boxes, track_ids,confidence):
                if conf >= 0.85:
                    lat, lon = serve_object_coords(
                        box, frame.shape,
                        drone_pos["lat"], drone_pos["long"],
                        drone_pos["alt"], drone_heading
                    )
                    x1, y1, x2, y2 = box

                    # 3. Crop the square directly from the numpy array (in memory)
                    # Note: NumPy slicing is [y_start:y_end, x_start:x_end]
                    gcp_square = self.newest_frame[y1:y2, x1:x2]

                    # 4. Pass the cropped array straight to your classifier
                    image = preprocess_image(gcp_square)
                    predictions = self.classifer.predict(image)
                    class_probabilities = predictions[0]
                    predicted_class_id = np.argmax(class_probabilities)
                    classified_objects.append((predicted_class_id, lat, lon, 0))

        return classified_objects

                # write to text file


    # ================================================================== #
    #  DEDUPLICATION MERGE                                                 #
    # ================================================================== #
    def _merge_detections(self, new_detections: list[tuple]) -> int:
        """
        Append each candidate to gcp_squares only when it is farther than
        GCP_DEDUP_MIN_DIST_M metres from every already-confirmed target.

        Iterates new_detections (never mutated) and only appends to
        gcp_squares — no mutation-during-iteration.

        Returns the count of genuinely new targets added.
        """
        added = 0
        for candidate in new_detections:
            is_duplicate = any(
                haversine_distance(existing, candidate) <= self.GCP_DEDUP_MIN_DIST_M
                for existing in self.gcp_squares
            )
            if not is_duplicate:
                self.gcp_squares.append(candidate)
                added += 1
        return added

    # ================================================================== #
    #  TSP SOLVERS                                                         #
    # ================================================================== #
    def _tsp_brute_force(self, start: tuple, targets: list[tuple]) -> list[tuple]:
        """
        Exact O(n!) TSP. Safe for n ≤ 8 (max 40 320 permutations).
        Returns the complete ordered route starting from whichever target
        minimises total Haversine distance from start.
        """
        best_cost  = float('inf')
        best_order = targets[:]

        for perm in itertools.permutations(targets):
            cost = haversine_distance(start, perm[0])
            for i in range(len(perm) - 1):
                cost += haversine_distance(perm[i], perm[i + 1])
            if cost < best_cost:
                best_cost  = cost
                best_order = list(perm)

        return best_order

    # ================================================================== #
    #  LAWNMOWER SEARCH                                                    #
    # ================================================================== #
    async def lawnmower_search(self, lane_spacing_meters: float = 5):
        """
        Fly a boustrophedon (lawnmower) sweep inside the geofence polygon.
        Lanes are evenly spaced by lane_spacing_meters in latitude and
        clipped to polygon-edge intersections so the path never exits the
        geofence boundary.
        """
        if lane_spacing_meters <= 0:
            raise ValueError("lane_spacing_meters must be greater than 0.")

        if self.bounding is None or len(self.bounding) < 3:
            print("Lawnmower search skipped: insufficient geofence points.")
            return

        polygon_points = self._get_ordered_polygon_points(self.bounding)
        lats = [p[0] for p in polygon_points]
        min_lat, max_lat = min(lats), max(lats)

        center_lat_rad = math.radians((min_lat + max_lat) / 2.0)
        meters_per_degree_lat = (
            self.LAT_METERS_COEFF_A
            - self.LAT_METERS_COEFF_B * math.cos(2 * center_lat_rad)
            + self.LAT_METERS_COEFF_C * math.cos(4 * center_lat_rad)
        )
        lane_spacing_deg_lat = lane_spacing_meters / meters_per_degree_lat

        current_pos = await self.drone.get_position_deg()
        search_alt  = max(current_pos["alt"], self.MIN_ALT_METERS)

        lane_lats = [min_lat]
        lane_lat  = min_lat + lane_spacing_deg_lat
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
                start_long, end_long = min_long, max_long
            else:
                start_long, end_long = max_long, min_long

            await reposition_drone_deg(
                drone=self.drone, coordinates=[lat, start_long, search_alt])
            await reposition_drone_deg(
                drone=self.drone, coordinates=[lat, end_long,   search_alt])

    # ================================================================== #
    #  CAMERA CAPTURE LOOP                                                 #
    # ================================================================== #
    async def camera(self):
        """
        Continuously reads frames from the SIYI A8 Mini via V4L2 and stores
        the latest one in self.newest_frame at ~30 fps.
        cap.release() in a finally block prevents resource leaks.
        """
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not cap.isOpened():
            print("Error: Could not open camera at /dev/video0")
            return

        print("[Camera] Stream started at 1920×1080.")
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[Camera] Empty frame — check connections.")
                    break
                self.newest_frame = frame
                await asyncio.sleep(self.CAMERA_INTERVAL_S)
        finally:
            cap.release()
            print("[Camera] Stream released.")

    # ================================================================== #
    #  PIXEL-LEVEL TARGET CENTERING  (velocity control)                   #
    # ================================================================== #
    async def center_on_target(self, target_x: int, target_y: int,
                               frame_width: int, frame_height: int):
        """
        Issue NED velocity commands to bring a detected target to the
        centre of the camera frame.

          vx — forward/back  (camera Y error → drone X in NED)
          vy — left/right    (camera X error → drone Y in NED)
          vz — hold alt; ascend if below MIN_ALT_METERS (NED: -z = up)
        """
        error_x = target_x - frame_width  // 2
        error_y = target_y - frame_height // 2
        print(f"[Center] Error X: {error_x}  Error Y: {error_y}")

        if abs(error_x) < self.PIXEL_TOLERANCE:
            error_x = 0
        if abs(error_y) < self.PIXEL_TOLERANCE:
            error_y = 0

        vx = max(min(-error_y * self.GAIN, self.MAX_VEL), -self.MAX_VEL)
        vy = max(min(-error_x * self.GAIN, self.MAX_VEL), -self.MAX_VEL)

        current_alt = await self.drone.get_altitude()
        vz = -0.5 if current_alt < self.MIN_ALT_METERS else 0.0

        reposition_velocity(self.drone, vx=vx, vy=vy, vz=vz)

    # ================================================================== #
    #  POLYGON GEOMETRY HELPERS                                            #
    # ================================================================== #
    def _get_ordered_polygon_points(self, points: list) -> list:
        """Sort polygon vertices by polar angle around their centroid."""
        center_lat  = sum(p[0] for p in points) / len(points)
        center_long = sum(p[1] for p in points) / len(points)
        return sorted(
            points,
            key=lambda p: math.atan2(p[0] - center_lat, p[1] - center_long)
        )

    def _get_lane_longitude_bounds(self, lane_lat: float,
                                   polygon_points: list) -> list | None:
        """
        Find min/max longitudes where a horizontal line at lane_lat
        intersects the polygon edges.
        Returns [min_long, max_long] or None if the lane misses the polygon.
        """
        intersections: list[float] = []
        lat_tol  = self.LANE_LAT_TOLERANCE_DEG
        long_tol = self.LANE_LONG_TOLERANCE_DEG
        size     = len(polygon_points)

        for idx in range(size):
            lat_1, long_1 = polygon_points[idx]
            lat_2, long_2 = polygon_points[(idx + 1) % size]

            if abs(lat_2 - lat_1) <= lat_tol:           # horizontal edge
                if abs(lane_lat - lat_1) <= lat_tol:
                    intersections.extend([min(long_1, long_2),
                                          max(long_1, long_2)])
                continue

            if not (min(lat_1, lat_2) - lat_tol         # lane outside span
                    <= lane_lat
                    <= max(lat_1, lat_2) + lat_tol):
                continue

            t = (lane_lat - lat_1) / (lat_2 - lat_1)
            intersections.append(long_1 + t * (long_2 - long_1))

        if len(intersections) < 2:
            return None

        intersections.sort()
        unique = [intersections[0]]
        for c in intersections[1:]:
            if abs(c - unique[-1]) > long_tol:
                unique.append(c)

        return [unique[0], unique[-1]] if len(unique) >= 2 else None


# ---------------------------------------------------------------------- #
#  Module-level utility                                                    #
# ---------------------------------------------------------------------- #
def pixel_to_world(cx: float, cy: float,
                   map_width: float, map_height: float,
                   world_width: float, world_height: float) -> tuple[float, float]:
    """Map pixel coordinates to world-space coordinates."""
    return (cx / map_width) * world_width, (cy / map_height) * world_height
