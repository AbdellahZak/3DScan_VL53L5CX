import serial
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import threading
import queue

# --- Configuration ---
SERIAL_PORT = 'COM5'  # Change to your ESP32 port (e.g., '/dev/ttyUSB0' on Linux/Mac)
BAUD_RATE = 115200  # Match your ESP32 baud rate
FOV_DEG = 65  # Your specified FoV
GRID_SIZE = 8  # Assuming 8x8 zones (64 points)
MAX_DISTANCE = 4000  # Max range in mm for plot scaling (adjust as needed)

# --- Math Setup ---
# Pre-calculate angle vectors to save processing time in the loop
fov_rad = np.deg2rad(FOV_DEG)
u = np.linspace(-1, 1, GRID_SIZE)
v = np.linspace(1, -1, GRID_SIZE)  # Top to bottom
U, V = np.meshgrid(u, v)

# Calculate direction vectors for each pixel (Pinhole model)
# We calculate the (x, y, z) unit vector for each of the 64 zones
# Tangent of the half-angle gives us the spread on the normalized plane
tan_x = U * np.tan(fov_rad / 2)
tan_y = V * np.tan(fov_rad / 2)

# Normalize these directions
# Vector D = (tan_x, tan_y, 1)
# Normalized D = D / |D|
norm = np.sqrt(tan_x ** 2 + tan_y ** 2 + 1)
dir_x = tan_x / norm
dir_y = tan_y / norm
dir_z = 1.0 / norm  # The forward component

# Flatten for easy multiplication with the distance list
dir_x_flat = dir_x.flatten()
dir_y_flat = dir_y.flatten()
dir_z_flat = dir_z.flatten()

# --- Serial Reader Thread ---
# We use a separate thread to read Serial so the GUI doesn't freeze
data_queue = queue.Queue(maxsize=1)
latest_distances = None


def read_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
    except Exception as e:
        print(f"Error connecting to serial: {e}")
        return

    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
            if line.startswith('{') and line.endswith('}'):
                try:
                    data = json.loads(line)
                    if 'distances' in data and len(data['distances']) == 64:
                        # Put new data in queue (overwrite old if full)
                        if data_queue.full():
                            try:
                                data_queue.get_nowait()
                            except queue.Empty:
                                pass
                        data_queue.put(data['distances'])
                except json.JSONDecodeError:
                    pass  # Ignore partial/corrupt lines
        except Exception as e:
            print(f"Serial Error: {e}")
            break


# Start the serial thread
thread = threading.Thread(target=read_serial, daemon=True)
thread.start()

# --- Visualization ---
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Initial empty line collection (distance vectors without arrowheads)
zeros = np.zeros(GRID_SIZE * GRID_SIZE)
initial_segments = np.zeros((GRID_SIZE * GRID_SIZE, 2, 3))
line_collection = Line3DCollection(initial_segments, colors='k', linewidths=1.0)
ax.add_collection3d(line_collection)

# Draw the "frustum" (cone) boundaries for visual reference
ax.set_xlim(-MAX_DISTANCE / 2, MAX_DISTANCE / 2)
ax.set_ylim(0, MAX_DISTANCE)  # Depth axis
ax.set_zlim(-MAX_DISTANCE / 2, MAX_DISTANCE / 2)
ax.set_xlabel('Horizontal (mm)')
ax.set_ylabel('Depth (mm)')
ax.set_zlabel('Vertical (mm)')
ax.set_title(f'Live ToF Vector Cloud ({FOV_DEG} deg FoV)')


def update(frame):
    global latest_distances
    global line_collection
    while not data_queue.empty():
        latest_distances = data_queue.get_nowait()
    if latest_distances is not None:
        d = np.array(latest_distances)
        # 1. Calculate Cartesian Coordinates
        # X, Y, Z = distance * direction_vector
        # Note: We map Sensor Z (Depth) -> Plot Y
        #       Sensor X (Horizontal) -> Plot X
        #       Sensor Y (Vertical) -> Plot Z

        X = d * dir_x_flat
        Y = d * dir_z_flat  # Depth
        Z = d * dir_y_flat

        # 2. Update line segments (from origin to each point)
        segments = np.zeros((GRID_SIZE * GRID_SIZE, 2, 3))
        segments[:, 1, 0] = X
        segments[:, 1, 1] = Y
        segments[:, 1, 2] = Z
        colors = plt.get_cmap('turbo')(np.clip(d / MAX_DISTANCE, 0, 1))
        line_collection.set_segments(segments)
        line_collection.set_color(colors)

    return line_collection,


# Animate
# interval=50 means 20 FPS target (adjust based on your PC speed)
ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)

plt.show()
