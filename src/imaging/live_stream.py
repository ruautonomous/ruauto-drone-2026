import cv2

# On Jetson, cam_id is usually 0 or 1
cam_id = 0

# Initialize capture
# We try V4L2 first as it's standard for the SIYI A8 Mini
cap = cv2.VideoCapture(cam_id, cv2.CAP_V4L2)

# Set the resolution to match your SIYI output
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print(f"Error: Could not open camera at /dev/video{cam_id}")
    exit()

print("Stream Started. Press 'q' to exit.")

# Create a named window and resize it so it fits your monitor
cv2.namedWindow("SIYI Live Feed", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Empty frame received. Check connections.")
        break

    # Display the resulting frame
    cv2.imshow("SIYI Live Feed", frame)

    # Use waitKey(1) to keep the window responsive
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
