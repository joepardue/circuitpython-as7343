# test_basic.py
# Basic AS7343 initialization and property testing
# Copy this to code.py to test basic functionality

import board
import time
from as7343 import AS7343, GAIN_0_5X, GAIN_1X, GAIN_4X, GAIN_64X, GAIN_256X, GAIN_2048X

print("=== AS7343 Basic Test ===")
print("Testing initialization and property API")

# Initialize I2C and sensor
try:
    i2c = board.STEMMA_I2C()
    sensor = AS7343(i2c)
    print("PASS Sensor initialized successfully")
except Exception as e:
    print(f"FAIL Initialization failed: {e}")
    raise

# Test 1: Check default values
print("\n--- Test 1: Default Values ---")
print(f"Default gain: {sensor.gain} (expected: {GAIN_4X})")
print(f"Default integration time: {sensor.integration_time} (expected: 150000)")

# Test 2: Gain property setting and getting
print("\n--- Test 2: Gain Property ---")
test_gains = [GAIN_0_5X, GAIN_1X, GAIN_4X, GAIN_64X, GAIN_256X, GAIN_2048X]
gain_names = ["0.5x", "1x", "4x", "64x", "256x", "2048x"]

for gain, name in zip(test_gains, gain_names):
    try:
        sensor.gain = gain
        readback = sensor.gain
        if readback == gain:
            print(f"PASS Gain {name}: Set={gain}, Read={readback}")
        else:
            print(f"FAIL Gain {name}: Set={gain}, Read={readback}")
    except Exception as e:
        print(f"FAIL Gain {name} failed: {e}")

# Test 3: Invalid gain handling
print("\n--- Test 3: Invalid Gain Handling ---")
try:
    sensor.gain = 0xFF  # Invalid value
    print("FAIL Invalid gain accepted (should have raised ValueError)")
except ValueError as e:
    print(f"PASS Invalid gain properly rejected: {e}")
except Exception as e:
    print(f"FAIL Unexpected error: {e}")

# Test 4: Integration time property
print("\n--- Test 4: Integration Time Property ---")
test_times = [10000, 50000, 100000, 150000, 200000]

for test_time in test_times:
    try:
        sensor.integration_time = test_time
        readback = sensor.integration_time
        if readback == test_time:
            print(f"PASS Integration time {test_time}us: Set={test_time}, Read={readback}")
        else:
            print(f"WARN Integration time {test_time}us: Set={test_time}, Read={readback}")
    except Exception as e:
        print(f"FAIL Integration time {test_time}us failed: {e}")

# Test 5: Invalid integration time handling
print("\n--- Test 5: Invalid Integration Time Handling ---")
try:
    sensor.integration_time = 999999999  # Way too long
    print("FAIL Invalid integration time accepted (should have raised ValueError)")
except ValueError as e:
    print(f"PASS Invalid integration time properly rejected: {e}")
except Exception as e:
    print(f"FAIL Unexpected error: {e}")

# Test 6: Power management basics
print("\n--- Test 6: Power Management ---")
try:
    sensor.shutdown()
    print("PASS Shutdown executed")
    time.sleep(0.1)
    
    sensor.wake()
    print("PASS Wake executed")
    time.sleep(0.1)
    
    # Restore settings after wake
    sensor.gain = GAIN_4X
    sensor.integration_time = 150000
    print("PASS Settings restored after wake")
    
except Exception as e:
    print(f"FAIL Power management failed: {e}")

# Test 7: Low power mode
print("\n--- Test 7: Low Power Mode ---")
try:
    sensor.enable_low_power_mode(True)
    print("PASS Low power mode enabled")
    
    sensor.enable_low_power_mode(False)
    print("PASS Low power mode disabled")
    
except Exception as e:
    print(f"FAIL Low power mode failed: {e}")

print("\n=== Basic Test Complete ===")
print("If all tests show PASS, basic functionality is working!")
print("Next: Run test_smux.py")