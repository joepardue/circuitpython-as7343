# test_measurement.py
# AS7343 measurement functionality testing
# Copy this to code.py to test measurement functions

import board
import time
from as7343 import AS7343, GAIN_4X

print("=== AS7343 Measurement Test ===")
print("Testing full measurement functionality")

# Initialize I2C and sensor
try:
    i2c = board.STEMMA_I2C()
    sensor = AS7343(i2c)
    print("PASS Sensor initialized successfully")
except Exception as e:
    print(f"FAIL Initialization failed: {e}")
    raise

# Set known good settings
sensor.gain = GAIN_4X
sensor.integration_time = 100000
print("PASS Test settings applied")

# Test 1: Start/stop measurement
print("\n--- Test 1: Start/Stop Measurement ---")
try:
    sensor.start_measurement()
    print("PASS Start measurement executed")
    time.sleep(0.2)
    
    sensor.stop_measurement()
    print("PASS Stop measurement executed")
    
except Exception as e:
    print(f"FAIL Start/stop measurement failed: {e}")

# Test 2: read_all() function
print("\n--- Test 2: Complete Spectral Scan (read_all) ---")
try:
    print("Taking complete spectral measurement...")
    start_time = time.monotonic()
    
    data = sensor.read_all()
    
    end_time = time.monotonic()
    duration = end_time - start_time
    
    print(f"PASS read_all() completed in {duration:.2f} seconds")
    print(f"PASS Got {len(data)} channels")
    
    # Show all channels and values
    print("Spectral data:")
    for channel, value in sorted(data.items()):
        print(f"  {channel}: {value}")
    
    # Check for expected channels
    expected_channels = {'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 
                        'FZ', 'FY', 'FXL', 'NIR', 'CLR'}
    actual_channels = set(data.keys())
    
    missing = expected_channels - actual_channels
    extra = actual_channels - expected_channels
    
    if not missing and not extra:
        print("PASS All expected channels present, no extras")
    else:
        if missing:
            print(f"WARN Missing channels: {missing}")
        if extra:
            print(f"INFO Extra channels: {extra}")
            
except Exception as e:
    print(f"FAIL read_all() failed: {e}")

# Test 3: data property
print("\n--- Test 3: Data Property ---")
try:
    # The data property should return the last measurement
    property_data = sensor.data
    
    if property_data == data:
        print("PASS Data property matches last read_all() result")
    else:
        print("FAIL Data property doesn't match last measurement")
        print(f"  Property keys: {list(property_data.keys())}")
        print(f"  Direct keys: {list(data.keys())}")
        
except Exception as e:
    print(f"FAIL Data property test failed: {e}")

# Test 4: channels property
print("\n--- Test 4: Channels Property ---")
try:
    channels_list = sensor.channels
    expected_order = ["F1", "F2", "FZ", "F3", "F4", "F5", "FY", "FXL", 
                     "F6", "F7", "F8", "NIR", "CLR"]
    
    print(f"Channels property returned {len(channels_list)} values")
    print("Channel order and values:")
    for i, (expected_label, value) in enumerate(zip(expected_order, channels_list)):
        print(f"  {i}: {expected_label} = {value}")
    
    if len(channels_list) == len(expected_order):
        print("PASS Channels property returned correct number of values")
    else:
        print(f"FAIL Expected {len(expected_order)} values, got {len(channels_list)}")
        
    # Check if values match data property where available
    mismatches = 0
    for label, list_value in zip(expected_order, channels_list):
        if label in sensor.data:
            if list_value != sensor.data[label]:
                mismatches += 1
                print(f"  WARN {label}: list={list_value}, data={sensor.data[label]}")
    
    if mismatches == 0:
        print("PASS Channels list values match data property")
    else:
        print(f"WARN {mismatches} value mismatches between channels and data")
        
except Exception as e:
    print(f"FAIL Channels property test failed: {e}")

# Test 5: Measurement repeatability
print("\n--- Test 5: Measurement Repeatability ---")
try:
    # Take multiple measurements and check consistency
    measurements = []
    print("Taking 3 measurements to check repeatability...")
    
    for i in range(3):
        data = sensor.read_all()
        measurements.append(data)
        print(f"  Measurement {i+1}: {len(data)} channels")
        time.sleep(0.1)
    
    # Check channel consistency
    all_same_channels = True
    first_channels = set(measurements[0].keys())
    
    for i, measurement in enumerate(measurements[1:], 1):
        if set(measurement.keys()) != first_channels:
            all_same_channels = False
            print(f"FAIL Measurement {i+1} has different channels")
            
    if all_same_channels:
        print("PASS All measurements have same channels")
    
    # Check value stability (allow some variation)
    max_variation = {}
    for channel in first_channels:
        values = [m[channel] for m in measurements]
        max_variation[channel] = max(values) - min(values)
    
    total_variation = sum(max_variation.values())
    avg_variation = total_variation / len(max_variation)
    
    print(f"Average variation across channels: {avg_variation:.1f}")
    
    if avg_variation < 100:  # Allow reasonable variation
        print("PASS Measurements are reasonably stable")
    else:
        print("WARN Measurements show significant variation")
        # Show worst channels
        worst = sorted(max_variation.items(), key=lambda x: x[1], reverse=True)[:3]
        for channel, variation in worst:
            print(f"  {channel}: varies by {variation}")
    
except Exception as e:
    print(f"FAIL Repeatability test failed: {e}")

# Test 6: Performance timing
print("\n--- Test 6: Performance Timing ---")
try:
    times = []
    print("Measuring read_all() performance...")
    
    for i in range(5):
        start = time.monotonic()
        sensor.read_all()
        end = time.monotonic()
        duration = end - start
        times.append(duration)
        print(f"  Measurement {i+1}: {duration:.2f}s")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Timing summary:")
    print(f"  Average: {avg_time:.2f}s")
    print(f"  Range: {min_time:.2f}s - {max_time:.2f}s")
    
    # Reasonable performance expectations
    if avg_time < 2.0:
        print("PASS Performance is good")
    elif avg_time < 5.0:
        print("WARN Performance is acceptable but slow")
    else:
        print("FAIL Performance is too slow")
        
except Exception as e:
    print(f"FAIL Performance test failed: {e}")

print("\n=== Measurement Test Complete ===")
print("Full measurement functionality verified!")
print("Next: Run test_power.py")