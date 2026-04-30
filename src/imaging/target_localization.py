#import cv2
import numpy as np
#from ultralytics import YOLO

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
    x = (cx / map_width) * world_width
    y = (cy / map_height) * world_height
    return x, y


# ------------------------------------- EVERYTHING ABOVE HAS BEEN IMPORTED TO OFFICIAL FILE
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="data.yaml",
    epochs=100,
    imgsz=640
)

"""lets say we get a list of ordered pairs of pixel values"""

ordered_pairs = ((100,100), (200,200), (300,300), (400,400),)

import math

current_position = (1,0)
print(current_position[0])

def mean_distance(self, current_position_arg): # Renamed current_position to current_position_arg to avoid global variable confusion
  return math.sqrt((float(current_position_arg[0]) - self[0])**2 + (float(current_position_arg[1]) - self[1])**2)

closest_node = (1000,1000)
arranged_graph = [] # Changed to a list for mutability

# Make a mutable copy of ordered_pairs if you intend to modify it
ordered_points_to_process = list(ordered_pairs)

for j in range(math.factorial(len(ordered_points_to_process))):
  if not ordered_points_to_process:
    break # No more points to process

  closest_node_current_iteration = None
  min_distance = float('inf')

  for i in ordered_points_to_process:
    distance_to_i = mean_distance(i, current_position)
    if distance_to_i < min_distance:
      min_distance = distance_to_i
      closest_node_current_iteration = i

  if closest_node_current_iteration is not None:
    arranged_graph.append(closest_node_current_iteration)
    ordered_points_to_process.remove(closest_node_current_iteration) # Correct way to remove an element from a list
    current_position = closest_node_current_iteration
  else:
    break # Should not happen if ordered_points_to_process is not empty

class Edge:
    def __init__(self, u, v, weight):
        self.u = u
        self.v = v
        self.weight = weight

    def __lt__(self, other):
        return self.weight < other.weight


n = 4  # number of vertices (number of gcp squares)

edges = [ # this will be the graph representation of the gcp squares
    Edge(0, 1, 10),
    Edge(0, 2, 6),
    Edge(0, 3, 5),
    Edge(1, 3, 15),
    Edge(2, 3, 4)
]

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

from pymavlink import mavutil
import time
import math

# --------------------------------
# CONNECT TO VEHICLE
# --------------------------------
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print("Connected to vehicle")

# --------------------------------
# CONSTANTS
# --------------------------------
MIN_ALT_METERS = 15   # 30 feet
PIXEL_TOLERANCE = 20     # pixels deadband
GAIN = 0.002             # velocity scaling factor
MAX_VEL = 1.0            # m/s cap

# --------------------------------
# FUNCTION: Get Relative Altitude
# --------------------------------
def get_altitude():
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    alt = msg.relative_alt / 1000.0
    return alt

# --------------------------------
# FUNCTION: Send Velocity Command (BODY FRAME)
# --------------------------------
def send_velocity_body(vx, vy, vz):
    master.mav.set_position_target_local_ned_send(
        0,
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b0000111111000111,  # velocity only
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0
    )

# --------------------------------
# MAIN CENTERING FUNCTION
# --------------------------------
def center_on_target(target_x, target_y, frame_width, frame_height):

    frame_center_x = frame_width // 2
    frame_center_y = frame_height // 2

    error_x = target_x - frame_center_x
    error_y = target_y - frame_center_y

    print("Error X:", error_x, "Error Y:", error_y)

    # Deadband (prevents oscillation)
    if abs(error_x) < PIXEL_TOLERANCE:
        error_x = 0
    if abs(error_y) < PIXEL_TOLERANCE:
        error_y = 0

    # Convert to velocity
    vx = -error_y * GAIN   # forward/back
    vy = -error_x * GAIN   # left/right
    vz = 0                 # hold altitude

    # Clamp velocity
    vx = max(min(vx, MAX_VEL), -MAX_VEL)
    vy = max(min(vy, MAX_VEL), -MAX_VEL)

    # Enforce minimum altitude
    current_alt = get_altitude()
    if current_alt < MIN_ALT_METERS:
        vz = -0.5  # ascend slightly
    else:
        vz = 0

    send_velocity_body(vx, vy, vz)

# --------------------------------
# LOOP EXAMPLE
# --------------------------------

for i in range(len(arranged_graph)):

    target_x = arranged_graph[i][0]
    target_y = arranged_graph[i][1]

    frame_width = 640
    frame_height = 480

    center_on_target(target_x, target_y, frame_width, frame_height)

    time.sleep(0.1)
