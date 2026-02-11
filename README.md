# ESP32 + VL53 3D ToF Viewer (...Progress)

Live 3D point cloud visualization for an 8x8 Time-of-Flight (ToF) sensor streamed from an ESP32 over serial.

## Project Snapshot

![Image](https://github.com/user-attachments/assets/8f82452c-a3d0-47f3-bcaa-1f163241a22d)![Live 3D viewer](docs/images/viewer.png)
![Image](https://github.com/user-attachments/assets/7d3c798c-a67d-4922-8234-53d8318355f9)


## Hardware

- ESP32 development board
- VL53 ToF sensor module (8x8 zones)
- USB cable
- Jumper wires
- BreadBoard

## Wiring (ESP32 <-> VL53)


| ESP32 Pin | VL53 Pin | Notes |
| --- | --- | --- |
| 3V3 | AVDD | Power |
| GND | GND | Common ground |
| GPIO21 (SDA) | SDA | I2C data |
| GPIO22 (SCL) | SCL | I2C clock |
| GPIO19 | LPN | I2c Enable pin |
| 3V3 | PWREN | power enable pulled high |

## Data Format

The Python viewer expects JSON lines with a 64-length `distances` array (millimeters):

```json
{"distances":[123,124,125, ... 64 values ...]}
```

## Setup

Install Python dependencies:

```bash
pip install pyserial numpy matplotlib
```

Update the serial port in `3D viewer script.py`:

```python
SERIAL_PORT = "COM5"
```

## Run

```bash
python "3D viewer script.py"
```

## Notes

- The viewer uses a 65° field of view and 8x8 grid by default.
- Adjust `MAX_DISTANCE` to match your sensor range for better visuals.

## Incoming Features
-adding filters and better vizualasation.
-Adding an IMU 
