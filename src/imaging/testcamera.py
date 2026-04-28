import cv2
import time

# 1. Setup the RTSP URL
# Make sure this matches what worked in VLC
rtsp_url = "rtsp://192.168.144.25:8554/main.264"

# 2. Initialize Video Capture
# For Jetson, GStreamer is faster, but this is the standard way:
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Error: Could not open SIYI stream.")
    exit()

# 3. Get Stream Properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30 # Standard for SIYI A8 mini

# 4. Define the Codec and Output File
# 'mp4v' or 'XVID' work well on Linux/Jetson
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('drone_flight_log.mp4', fourcc, fps, (frame_width, frame_height))

print("Recording started... Press 'q' to stop.")

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Dropped frame or stream interrupted.")
            break

        # Write the frame to the file on the Jetson
        out.write(frame)

        # Optional: Display the window (Slows down Jetson, comment out for flight)
        cv2.imshow('SIYI Recording', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # 5. Clean up
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Recording saved successfully.")