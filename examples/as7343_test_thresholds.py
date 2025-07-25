# test_thresholds.py
# AS7343 threshold detection and saturation testing
# Copy this to code.py to test threshold functionality

import board
import time
from as7343 import AS7343, GAIN_4X, GAIN_64X, GAIN_256X

print("=== AS7343 Threshold Test ===")
print("Testing check_thresholds() and saturation detection")

# Initialize I2C and sensor
try:
    i2c = board.STEMMA_I2C()
    sensor = AS7343(i2c)
    print("PASS Sensor initialized successfully")
except Exception as e:
    print(f"FAIL Initialization failed: {e}")
    raise

# Test 1: Basic threshold checking with mock data
print("\n--- Test 1: Basic Threshold Checking ---")
mock_data = {
    'F1': 1000,
    'F2': 2000,
    'F3': 3000,
    'F4': 4000,
    'F5': 5000,
    'F6': 6000,
    'F7': 7000,
    'F8': 8000,
    'FZ': 500,
    'FY': 1500,
    'FXL': 2500,
    'NIR': 3500,
    'CLR': 4500
}

try:
    # Test with threshold of 3000
    flagged = sensor.check_thresholds(3000, mock_data)
    expected_count = 8  # F3, F4, F5, F6, F7, F8, NIR, CLR
    if len(flagged) == expected_count:
        print(f"PASS Threshold 3000: Found {len(flagged)} channels above threshold")
        for label, value in flagged:
            print(f"  {label}: {value}")
    else:
        print(f"FAIL Threshold 3000: Expected {expected_count}, got {len(flagged)}")
except Exception as e:
    print(f"FAIL Basic threshold test failed: {e}")

# Test 2: Edge case - threshold higher than all values
print("\n--- Test 2: High Threshold Edge Case ---")
try:
    flagged = sensor.check_thresholds(10000, mock_data)
    if len(flagged) == 0:
        print("PASS High threshold: No channels flagged (expected)")
    else:
        print(f"FAIL High threshold: {len(flagged)} channels unexpectedly flagged")
except Exception as e:
    print(f"FAIL High threshold test failed: {e}")

# Test 3: Edge case - threshold of 0
print("\n--- Test 3: Zero Threshold Edge Case ---")
try:
    flagged = sensor.check_thresholds(0, mock_data)
    if len(flagged) == len(mock_data):
        print("PASS Zero threshold: All channels flagged (expected)")
    else:
        print(f"FAIL Zero threshold: {len(flagged)} of {len(mock_data)} channels flagged")
except Exception as e:
    print(f"FAIL Zero threshold test failed: {e}")

# Test 4: Error handling - invalid data types
print("\n--- Test 4: Invalid Data Type Handling ---")
invalid_data = {
    'F1': 1000,
    'F2': 'invalid',
    'F3': 3000,
    'F4': None,
    'F5': 5000.5,
    'F6': 6000
}

try:
    flagged = sensor.check_thresholds(2000, invalid_data)
    # Should handle gracefully and only process valid integers
    valid_flagged = [(label, val) for label, val in flagged if isinstance(val, int)]
    print(f"PASS Invalid data handling: Processed {len(valid_flagged)} valid channels")
    print("  Expected type warnings printed above")
except Exception as e:
    print(f"FAIL Invalid data handling failed: {e}")

# Test 5: Error handling - invalid threshold types
print("\n--- Test 5: Invalid Threshold Type Handling ---")
try:
    flagged = sensor.check_thresholds('invalid', mock_data)
    print("FAIL Invalid threshold type accepted (should fail gracefully)")
except Exception as e:
    print(f"PASS Invalid threshold type properly handled: {e}")

# Test 6: Empty data handling
print("\n--- Test 6: Empty Data Handling ---")
try:
    flagged = sensor.check_thresholds(1000, {})
    if len(flagged) == 0:
        print("PASS Empty data: No channels flagged (expected)")
    else:
        print(f"FAIL Empty data: {len(flagged)} channels unexpectedly flagged")
except Exception as e:
    print(f"FAIL Empty data test failed: {e}")

# Test 7: Saturation detection with real sensor data
print("\n--- Test 7: Saturation Detection with Real Data ---")
try:
    # Set high gain to potentially cause saturation
    sensor.gain = GAIN_256X
    sensor.integration_time = 180000
    
    print("Taking measurement with high gain...")
    sensor.read_all()
    real_data = sensor.data
    
    # Check for saturation (near 16-bit max)
    saturation_threshold = 60000  # Conservative saturation threshold
    saturated = sensor.check_thresholds(saturation_threshold, real_data)
    
    if len(saturated) > 0:
        print(f"WARN Saturation detected in {len(saturated)} channels:")
        for label, value in saturated:
            print(f"  {label}: {value}")
        print("  Consider reducing gain or integration time")
    else:
        print("PASS No saturation detected at current settings")
        
except Exception as e:
    print(f"FAIL Saturation detection failed: {e}")

# Test 8: Using default data (sensor.data property)
print("\n--- Test 8: Default Data Property Usage ---")
try:
    # Ensure we have recent data
    sensor.gain = GAIN_4X
    sensor.integration_time = 150000
    sensor.read_all()
    
    # Test without providing data parameter (should use sensor.data)
    flagged = sensor.check_thresholds(1000)  # No data parameter
    print(f"PASS Default data usage: {len(flagged)} channels above 1000")
    
    # Verify it matches explicit data parameter
    flagged_explicit = sensor.check_thresholds(1000, sensor.data)
    if len(flagged) == len(flagged_explicit):
        print("PASS Default data matches explicit data parameter")
    else:
        print("FAIL Default data does not match explicit parameter")
        
except Exception as e:
    print(f"FAIL Default data test failed: {e}")

# Test 9: Maximum value detection
print("\n--- Test 9: Maximum Value Detection ---")
max_data = {f'F{i}': 65535 for i in range(1, 9)}  # 16-bit max values
max_data.update({'FZ': 65535, 'FY': 65535, 'FXL': 65535, 'NIR': 65535, 'CLR': 65535})

try:
    flagged = sensor.check_thresholds(65534, max_data)
    if len(flagged) == len(max_data):
        print("PASS Maximum value detection: All channels at max flagged")
    else:
        print(f"FAIL Maximum value detection: {len(flagged)} of {len(max_data)} flagged")
except Exception as e:
    print(f"FAIL Maximum value test failed: {e}")

# Test 10: Performance with multiple threshold checks
print("\n--- Test 10: Performance Test ---")
try:
    start_time = time.monotonic()
    
    # Perform multiple threshold checks
    for threshold in [100, 500, 1000, 2000, 5000]:
        sensor.check_thresholds(threshold, mock_data)
    
    end_time = time.monotonic()
    duration = end_time - start_time
    
    if duration < 1.0:  # Should be very fast
        print(f"PASS Performance test: {duration:.3f}s for 5 threshold checks")
    else:
        print(f"WARN Performance: {duration:.3f}s (may be slow)")
        
except Exception as e:
    print(f"FAIL Performance test failed: {e}")

print("\n=== Threshold Test Complete ===")
print("Review results above for any FAIL or WARN messages")
print("Saturation warnings are normal under bright light conditions")
print("Next: Check other test files for complete validation")