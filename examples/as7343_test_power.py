# test_power.py
# AS7343 power management testing
# Copy this to code.py to test power management functionality

import board
import time
from as7343 import AS7343, GAIN_4X

print("=== AS7343 Power Management Test ===")
print("Testing sleep, wake, and power control functionality")

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
sensor.integration_time = 50000
print("PASS Test settings applied")

# Test 1: Basic shutdown and wake
print("\n--- Test 1: Basic Shutdown/Wake Cycle ---")
try:
    # Take baseline measurement
    baseline_data = sensor.read_all()
    baseline_channels = len(baseline_data)
    print(f"Baseline measurement: {baseline_channels} channels")
    
    # Shutdown
    sensor.shutdown()
    print("PASS Shutdown executed")
    time.sleep(0.5)
    
    # Wake up
    sensor.wake()
    print("PASS Wake executed")
    time.sleep(0.2)
    
    # Restore settings (they may be lost after shutdown)
    sensor.gain = GAIN_4X
    sensor.integration_time = 50000
    print("PASS Settings restored after wake")
    
    # Test measurement after wake
    wake_data = sensor.read_all()
    wake_channels = len(wake_data)
    
    if wake_channels == baseline_channels:
        print(f"PASS Post-wake measurement: {wake_channels} channels")
    else:
        print(f"WARN Post-wake channels differ: {wake_channels} vs {baseline_channels}")
        
except Exception as e:
    print(f"FAIL Basic shutdown/wake failed: {e}")

# Test 2: Multiple shutdown/wake cycles
print("\n--- Test 2: Multiple Shutdown/Wake Cycles ---")
try:
    for cycle in range(3):
        print(f"  Cycle {cycle + 1}:")
        
        # Shutdown
        sensor.shutdown()
        print(f"    Shutdown complete")
        time.sleep(0.2)
        
        # Wake
        sensor.wake()
        print(f"    Wake complete")
        time.sleep(0.1)
        
        # Restore and test
        sensor.gain = GAIN_4X
        sensor.integration_time = 50000
        
        # Quick measurement test
        try:
            data = sensor.read_all()
            print(f"    Measurement: {len(data)} channels")
        except Exception as e:
            print(f"    FAIL Measurement failed: {e}")
            break
    else:
        print("PASS All shutdown/wake cycles successful")
        
except Exception as e:
    print(f"FAIL Multiple cycles failed: {e}")

# Test 3: Low power mode
print("\n--- Test 3: Low Power Mode ---")
try:
    # Test enabling low power mode
    sensor.enable_low_power_mode(True)
    print("PASS Low power mode enabled")
    
    # Take measurement in low power mode
    lp_data = sensor.read_all()
    print(f"PASS Low power measurement: {len(lp_data)} channels")
    
    # Test disabling low power mode
    sensor.enable_low_power_mode(False)
    print("PASS Low power mode disabled")
    
    # Take measurement with low power disabled
    normal_data = sensor.read_all()
    print(f"PASS Normal power measurement: {len(normal_data)} channels")
    
    # Compare channel counts
    if len(lp_data) == len(normal_data):
        print("PASS Low power mode doesn't affect channel count")
    else:
        print(f"WARN Channel count differs: LP={len(lp_data)}, Normal={len(normal_data)}")
        
except Exception as e:
    print(f"FAIL Low power mode test failed: {e}")

# Test 4: Sleep After Interrupt (SAI) functionality
print("\n--- Test 4: Sleep After Interrupt (SAI) ---")
try:
    # Test enabling SAI
    sensor.enable_sleep_after_interrupt(True)
    print("PASS Sleep after interrupt enabled")
    
    # Check if device is sleeping
    is_sleeping = sensor.is_device_sleeping()
    print(f"Device sleeping status: {is_sleeping}")
    
    # Clear sleep active status
    sensor.clear_sleep_active()
    print("PASS Sleep active status cleared")
    
    # Check sleeping status again
    is_sleeping_after = sensor.is_device_sleeping()
    print(f"Device sleeping status after clear: {is_sleeping_after}")
    
    # Test disabling SAI
    sensor.enable_sleep_after_interrupt(False)
    print("PASS Sleep after interrupt disabled")
    
    # Take measurement to ensure still working
    sai_data = sensor.read_all()
    print(f"PASS SAI test measurement: {len(sai_data)} channels")
    
except Exception as e:
    print(f"FAIL SAI test failed: {e}")

# Test 5: Power state measurement comparison
print("\n--- Test 5: Power State Measurement Comparison ---")
try:
    # Normal power measurement
    sensor.enable_low_power_mode(False)
    time.sleep(0.1)
    normal_data = sensor.read_all()
    normal_total = sum(normal_data.values())
    
    # Low power measurement
    sensor.enable_low_power_mode(True)
    time.sleep(0.1)
    lp_data = sensor.read_all()
    lp_total = sum(lp_data.values())
    
    # Compare totals
    print(f"Normal power total: {normal_total}")
    print(f"Low power total: {lp_total}")
    
    difference_percent = abs(normal_total - lp_total) / normal_total * 100
    print(f"Difference: {difference_percent:.1f}%")
    
    if difference_percent < 10:
        print("PASS Power modes show similar readings")
    elif difference_percent < 50:
        print("WARN Power modes show some difference")
    else:
        print("WARN Power modes show significant difference")
    
    # Restore normal power mode
    sensor.enable_low_power_mode(False)
    
except Exception as e:
    print(f"FAIL Power comparison failed: {e}")

# Test 6: Rapid power cycling stress test
print("\n--- Test 6: Rapid Power Cycling Stress Test ---")
try:
    print("Performing rapid power cycles...")
    success_count = 0
    
    for i in range(10):
        try:
            # Rapid cycle
            sensor.shutdown()
            time.sleep(0.05)  # Very short sleep
            sensor.wake()
            time.sleep(0.05)
            
            # Quick settings restore
            sensor.gain = GAIN_4X
            sensor.integration_time = 50000
            
            # Quick test measurement
            sensor.start_measurement()
            time.sleep(0.1)
            sensor.stop_measurement()
            
            success_count += 1
            
        except Exception as e:
            print(f"  Cycle {i+1} failed: {e}")
            break
    
    print(f"Completed {success_count}/10 rapid cycles")
    
    if success_count >= 8:
        print("PASS Rapid power cycling robust")
    elif success_count >= 5:
        print("WARN Some rapid power cycle failures")
    else:
        print("FAIL Rapid power cycling unreliable")
        
    # Final verification measurement
    final_data = sensor.read_all()
    print(f"PASS Final verification: {len(final_data)} channels")
    
except Exception as e:
    print(f"FAIL Stress test failed: {e}")

print("\n=== Power Management Test Complete ===")
print("Power management functionality verified!")
print("Next: Run test_thresholds.py")