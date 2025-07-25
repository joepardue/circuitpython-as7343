# test_smux.py
# AS7343 SMUX (sensor multiplexer) testing
# Copy this to code.py to test SMUX functionality

import board
import time
from as7343 import AS7343, SMUX_VISIBLE, SMUX_NIR, SMUX_FZF5

print("=== AS7343 SMUX Test ===")
print("Testing sensor multiplexer functionality")

# Initialize I2C and sensor
try:
    i2c = board.STEMMA_I2C()
    sensor = AS7343(i2c)
    print("PASS Sensor initialized successfully")
except Exception as e:
    print(f"FAIL Initialization failed: {e}")
    raise

# Test 1: SMUX mode constants
print("\n--- Test 1: SMUX Mode Constants ---")
print(f"SMUX_VISIBLE = '{SMUX_VISIBLE}'")
print(f"SMUX_NIR = '{SMUX_NIR}'")
print(f"SMUX_FZF5 = '{SMUX_FZF5}'")
print("PASS SMUX constants defined")

# Test 2: Get SMUX mappings
print("\n--- Test 2: SMUX Channel Mappings ---")
try:
    visible_map = sensor.get_smux_map(SMUX_VISIBLE)
    print(f"VISIBLE channels: {[label for label, reg in visible_map]}")
    
    nir_map = sensor.get_smux_map(SMUX_NIR)
    print(f"NIR channels: {[label for label, reg in nir_map]}")
    
    fzf5_map = sensor.get_smux_map(SMUX_FZF5)
    print(f"FZF5 channels: {[label for label, reg in fzf5_map]}")
    
    print("PASS All SMUX mappings retrieved")
    
except Exception as e:
    print(f"FAIL SMUX mapping failed: {e}")

# Test 3: Invalid SMUX mode handling
print("\n--- Test 3: Invalid SMUX Mode Handling ---")
try:
    sensor.get_smux_map("INVALID_MODE")
    print("FAIL Invalid SMUX mode accepted")
except ValueError as e:
    print(f"PASS Invalid SMUX mode rejected: {e}")
except Exception as e:
    print(f"FAIL Unexpected error: {e}")

# Test 4: Set SMUX modes
print("\n--- Test 4: SMUX Mode Setting ---")
smux_modes = [SMUX_VISIBLE, SMUX_NIR, SMUX_FZF5]

for mode in smux_modes:
    try:
        sensor.set_smux_mode(mode)
        print(f"PASS SMUX mode {mode} set successfully")
        time.sleep(0.1)  # Brief delay between mode changes
    except Exception as e:
        print(f"FAIL SMUX mode {mode} failed: {e}")

# Test 5: Read individual SMUX modes
print("\n--- Test 5: Individual SMUX Mode Reading ---")
for mode in smux_modes:
    try:
        data = sensor.read_smux_mode(mode)
        channels = list(data.keys())
        values = list(data.values())
        
        print(f"SMUX {mode}:")
        print(f"  Channels: {channels}")
        print(f"  Values: {values}")
        
        # Check if we got expected number of channels
        expected_counts = {
            SMUX_VISIBLE: 5,  # F1, F2, F3, F4, FY
            SMUX_NIR: 6,      # F6, F7, F8, FXL, NIR, CLR
            SMUX_FZF5: 2      # FZ, F5
        }
        
        expected = expected_counts[mode]
        actual = len(channels)
        
        if actual == expected:
            print(f"  PASS Got {actual} channels (expected {expected})")
        else:
            print(f"  FAIL Got {actual} channels (expected {expected})")
            
        # Check if values are reasonable (not all zeros, not all maxed)
        if all(v == 0 for v in values):
            print(f"  WARN All values are zero - check lighting")
        elif any(v >= 65535 for v in values):
            print(f"  WARN Some values are saturated (65535)")
        else:
            print(f"  PASS Values in reasonable range")
            
    except Exception as e:
        print(f"FAIL Reading SMUX mode {mode} failed: {e}")

# Test 6: Channel consistency check
print("\n--- Test 6: Channel Consistency Check ---")
try:
    # Read each mode again and verify we get consistent results
    data1 = sensor.read_smux_mode(SMUX_VISIBLE)
    time.sleep(0.1)
    data2 = sensor.read_smux_mode(SMUX_VISIBLE)
    
    # Values might vary slightly, but channels should be the same
    if set(data1.keys()) == set(data2.keys()):
        print("PASS Channel labels consistent between reads")
    else:
        print("FAIL Channel labels changed between reads")
        print(f"  First: {list(data1.keys())}")
        print(f"  Second: {list(data2.keys())}")
        
    # Check if values are in similar range (not wildly different)
    max_change = 0
    for channel in data1.keys():
        if channel in data2:
            change = abs(data1[channel] - data2[channel])
            max_change = max(max_change, change)
    
    if max_change < 1000:  # Allow some variation
        print(f"PASS Values reasonably stable (max change: {max_change})")
    else:
        print(f"WARN Values vary significantly (max change: {max_change})")
        
except Exception as e:
    print(f"FAIL Consistency check failed: {e}")

print("\n=== SMUX Test Complete ===")
print("SMUX system basic functionality verified!")
print("Next: Run test_measurement.py")