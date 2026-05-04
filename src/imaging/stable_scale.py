import gpiod
import time
import statistics
from hx711 import HX711

# --- CONFIGURATION ---
# Replace with your actual libgpiod line offsets!
DOUT_LINE = 144
SCK_LINE = 112

def main():
    print("Initializing stable hardware-accelerated HX711...")
    
    # 1. Connect to the hardware
    chip = gpiod.Chip("/dev/gpiochip0")
    hx = HX711(dout=DOUT_LINE, pd_sck=SCK_LINE, chip=chip)
    
    # 2. Reset the chip to ensure a clean slate
    hx.reset()
    
    try:
        print("Taking filtered readings. Press Ctrl+C to stop.\n")
        while True:
            samples = []
            
            # Take 11 extremely fast raw readings
            for _ in range(31):
                # .read() grabs a single raw value without any library averaging
                val = hx.read_long()
                if val is not False:
                    samples.append(val)
            
            if len(samples) > 0:
                # Calculate the median to completely ignore the extreme highs/lows
                stable_raw = statistics.median(samples)
                
                # Optional: Calculate the spread to monitor electrical noise
                noise_spread = max(samples) - min(samples)
                
                print(f"Stable Raw Value: {stable_raw:>8.0f}  (Noise spread: {noise_spread})")
            else:
                print("Error reading sensor.")
                
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\nExiting and cleaning up...")
        # Cleanly release the GPIO lines
        hx.power_down()

if __name__ == '__main__':
    main()
