import numpy as np
import cv2

from helper.constants import UNIT_TO_METERS, R_EARTH_IN_METERS
from helper.model_interface import DetectionModel


# Earth radius in meters
R_EARTH_IN_METERS = 6378137.0

def serve_object_coords(bbox: tuple, img_shape: tuple, lat: float, lon: float, alt: float, hdg: float):
    # 1. Sanitize Raw MAVLink Units safely
    actual_lat = lat / 1e7 if abs(lat) > 90.0 else lat
    actual_lon = lon / 1e7 if abs(lon) > 180.0 else lon
    actual_alt = alt / 1000.0 if alt > 1000 else alt
    actual_hdg_deg = hdg / 100.0 if hdg > 360 else hdg

    # 2. Pixel to Meter Scaling (Check your Gazebo .sdf to ensure 75.0 degrees is correct)
    gsd = 2 * actual_alt * np.tan(np.radians(75.0 / 2.0)) / img_shape[1]

    x1, y1, x2, y2 = bbox
    center_x = float((x1+x2) / 2)
    center_y = float((y1+y2) / 2)

    # Positive is Right, Positive is Forward
    dx_meters = gsd * (center_x - img_shape[1] / 2)
    dy_meters = gsd * (img_shape[0] / 2 - center_y)

    # 3. Standard 2D Geographic Rotation Matrix
    heading_rad = np.radians(actual_hdg_deg)
    d_lat_meters = dy_meters * np.cos(heading_rad) - dx_meters * np.sin(heading_rad)
    d_lon_meters = dy_meters * np.sin(heading_rad) + dx_meters * np.cos(heading_rad)

    # 4. Convert metric offsets back to decimal degrees
    meters_per_deg_lat = R_EARTH_IN_METERS * (np.pi / 180.0)
    meters_per_deg_lon = R_EARTH_IN_METERS * np.cos(np.radians(actual_lat)) * (np.pi / 180.0)

    final_lat = actual_lat + (d_lat_meters / meters_per_deg_lat)
    final_lon = actual_lon + (d_lon_meters / meters_per_deg_lon)

    # Return the absolute global coordinate
    return final_lat, final_lon

if __name__ == "__main__":
    # serve_object_coords("test_images/visdrone.jpg", -70, 40.49, 70, 0)
    model = DetectionModel("best_the_actual_dataset.pt")
    serve_object_coords("test_images/50ft.jpg", -70, 40.49, 50 * UNIT_TO_METERS, 0, model)
