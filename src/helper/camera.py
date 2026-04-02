import cv2
import time
import asyncio
from pymavlink import mavutil
from pymavlink.dialects.v20 import common
from utils.drone import Drone
class Camera:
     def __init__(self, drone: Drone):
         self.drone = drone
     def capture(self):
         cap = cv2.VideoCapture(0)
         _, frame = cap.read()
         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         cv2.imshow('frame', gray)
         if(cv2.waitKey(1) & 0xFF == ord('q')):
             cap.release()
             cv2.destroyAllWindows()
