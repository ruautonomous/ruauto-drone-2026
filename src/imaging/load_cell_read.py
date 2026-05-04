import socket

# Setup the listening socket
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
# Set a timeout so your main app doesn't freeze if the scale script stops
sock.settimeout(0.5) 

def get_current_weight():
    """Fetches the most recent broadcasted weight."""
    try:
        # Buffer size of 1024 bytes is plenty for a simple number
        data, addr = sock.recvfrom(1024) 
        # Decode the bytes back into a float/int
        return float(data.decode('utf-8'))
    except socket.timeout:
        print("Warning: No data received from scale broadcaster.")
        return None

# --- Your Main Application Logic ---
print("Main App (Venv) Running...")

while True:
    # You can call this anywhere in your app without worrying about hardware timing!
    current_weight = get_current_weight()
    
    if current_weight is not None:
        print(f"Main App received: {current_weight}")
        
    # Do whatever else your main app needs to do
