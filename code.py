# code.py - Example usage of AS7343 driver
import board
import busio
import time
import sys
from as7343 import AS7343

i2c = busio.I2C(board.SCL, board.SDA)
sensor = AS7343(i2c)

print("AS7343 initialized and communication verified.")
print("Type 'g' and press Enter to get a reading.")

while True:
    cmd = sys.stdin.readline().strip()
    if cmd == 'g':
        if sensor.data_ready():
            readings = sensor.read_fifo()
            if any(readings):
                print("--- AS7343 readings ---")
                print(f"Ch1: {readings[0]}")
                print(f"Ch2: {readings[1]}")
                print(f"Ch3: {readings[2]}")
                print(f"Ch4: {readings[3]}")
                print(f"Ch5: {readings[4]}")
                print(f"Ch6: {readings[5]}")
                print("------------------------")
            else:
                print("No valid data yet.")
        else:
            print("Data not ready.")
