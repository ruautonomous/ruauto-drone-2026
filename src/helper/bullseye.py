import cv2
import numpy as np
from google.colab.patches import cv2_imshow

def detect_bulleye(x, y):
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=100,
        param2=30,
        minRadius=10,
        maxRadius=200
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for x, y, r in circles[0]:
            print("Center:", x, y)
            print("Radius:", r)

    centers = []

    for circle in circles[0]:
        centers.append((circle[0], circle[1]))

    # Average center
    cx = int(np.mean([c[0] for c in centers]))
    cy = int(np.mean([c[1] for c in centers]))
    print("Final center:", (cx, cy))
    return cx, cy

def center_on_target(target_x, target_y, frame_width, frame_height):
    PIXEL_TOLERANCE = 20
    GAIN = 0.002
    MAX_VEL = 1.0

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
    return vx, vy, vz

    # Enforce minimum altitude
    #current_alt = drone.get_position_deg()[2]
    #if current_alt < 15:
        #vz = -0.5  # ascend slightly
    #else:
       # vz = 0

    #send_velocity_body(vx, vy, vz)
