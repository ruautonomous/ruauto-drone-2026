import numpy as np
import cv2

from helper.constants import UNIT_TO_METERS, R_EARTH_IN_METERS
from helper.model_interface import DetectionModel


def serve_object_coords(bbox: tuple, img_shape: tuple, lat: float, lon: float, alt: float, hdg: float):
    gsd = 2 * alt * np.tan(np.radians(75.0 / 2.0)) / img_shape[1]

    objects = []
    x1, y1, x2, y2 = bbox

    center_x = float((x1+x2) / 2)
    center_y = float((y1+y2) / 2)

    # Convert offsets to meters first
    dx_meters = gsd * (center_x - img_shape[1] / 2) # Positive is Right
    dy_meters = gsd * (img_shape[0] / 2 - center_y) # Positive is Forward

    heading_rad = np.radians(hdg)

    # Standard 2D rotation matrix
    # Assuming Heading 0 is North, and rotates clockwise
    d_lat_meters = dy_meters * np.cos(heading_rad) + dx_meters * np.sin(heading_rad)
    d_lon_meters = dx_meters * np.cos(heading_rad) - dy_meters * np.sin(heading_rad)

    # PREV BAD CODE (doesn't use hdg right)
    # d_lat_meters = gsd * (img_shape[0] / 2 - center_y) * np.sin(np.radians(hdg + 90))
    # d_lon_meters = gsd * (img_shape[1] / 2 - center_x) * np.cos(np.radians(hdg + 90))

    lat_shrinking_factor = R_EARTH_IN_METERS * np.pi / 180

    d_lat = d_lat_meters / lat_shrinking_factor
    d_lon = d_lon_meters / (lat_shrinking_factor * np.cos(np.radians(lat)))

    # objects.append({
    #     "name": name,
    #     "location": (lat + d_lat, lon + d_lon)
    # })

    return (lat + d_lat, lon + d_lon)


if __name__ == "__main__":
    # serve_object_coords("test_images/visdrone.jpg", -70, 40.49, 70, 0)
    model = DetectionModel("best_the_actual_dataset.pt")
    serve_object_coords("test_images/50ft.jpg", -70, 40.49, 50 * UNIT_TO_METERS, 0, model)
