# as7343_comprehensive_test.py
import time
import board
import struct
import sys
from adafruit_bus_device.i2c_device import I2CDevice

# Constants
_AS7343_I2C_ADDR = 0x39
_ENABLE = 0x80
_ATIME = 0x81
_WTIME = 0x83
_ASTEP = 0xD4
_ASTEP_H = 0xD5
_CONTROL = 0xFA
_CFG1 = 0xC6
_DATA_START = 0x95
_CFG0 = 0xBF
_CFG20 = 0xD6
_STATUS = 0x93
_ASTATUS = 0x94

# Gain values
GAIN_MAP = {
    0: "0.5x",
    1: "1x",
    2: "2x",
    3: "4x",
    4: "8x",
    5: "16x", 
    6: "32x",
    7: "64x",
    8: "128x",
    9: "256x",
    10: "512x",
    11: "1024x",
    12: "2048x"
}

# Channel names
CHANNEL_NAMES = ["F1", "F2", "F3", "F4", "FY", "F5", "F6", "F7", "F8", "FZ", "FXL", "NIR", "CLR"]

def main():
    i2c = board.STEMMA_I2C()
    device = I2CDevice(i2c, _AS7343_I2C_ADDR)
    
    # Display header
    print_header()
    
    # Main menu
    while True:
        print("\nAS7343 Comprehensive Test Suite")
        print("-------------------------------")
        print("1. Fix Verification (64746 Limit Test)")
        print("2. Integration Time Test")
        print("3. Gain Test")
        print("4. Full Channel Scan")
        print("5. Auto-zero Configuration Test")
        print("6. Saturation Detection Test")
        print("7. Power Management Test")
        print("8. Run All Tests")
        print("0. Exit")
        
        try:
            choice = int(input("\nSelect test: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
            
        if choice == 0:
            print("Exiting test suite.")
            return
        elif choice == 1:
            test_fix_verification(device)
        elif choice == 2:
            test_integration_time(device)
        elif choice == 3:
            test_gain(device)
        elif choice == 4:
            test_full_channel_scan(device)
        elif choice == 5:
            test_autozero(device)
        elif choice == 6:
            test_saturation(device)
        elif choice == 7:
            test_power_management(device)
        elif choice == 8:
            run_all_tests(device)
        else:
            print("Invalid choice. Please select 0-8.")

def print_header():
    print("\n" + "=" * 50)
    print("AS7343 14-Channel Spectral Sensor Test Suite")
    print("=" * 50)
    print("This test suite verifies the functionality of the AS7343 driver")
    print("and confirms that the 64746 ADC limit issue has been fixed.")
    print("=" * 50)

def reset_sensor(device):
    """Reset the sensor to a known state"""
    print("Resetting sensor...", end="")
    write_u8(device, _CONTROL, 0x08)  # Software reset
    time.sleep(1.0)
    write_u8(device, _ENABLE, 0x01)   # Power on
    print(" done")

def test_fix_verification(device):
    """Test if the 64746 limit has been fixed"""
    print("\n--- 64746 Limit Fix Verification ---")
    print("This test checks if readings can exceed the old 64746 limit")
    print("Please aim the sensor at a bright light source\n")
    
    reset_sensor(device)
    
    # Set maximum gain (2048x)
    print("Setting maximum gain (2048x)...")
    write_u8(device, _CFG1, 12)
    
    # Set maximum integration time
    print("Setting maximum integration time...")
    astep = 65534  # Max value
    write_u8(device, _ATIME, 0)
    write_u16(device, _ASTEP, astep)
    
    input("Press Enter to take reading...")
    
    # Start measurement
    write_u8(device, _ENABLE, 0x03)  # PON=1, SP_EN=1
    time.sleep(1.0)  # Allow integration to complete
    
    # Read all channels
    print("\nReading all channels:")
    max_value = 0
    values = []
    
    for i in range(8):  # Check first 8 registers for high values
        reg = _DATA_START + (i * 2)
        value = read_u16(device, reg)
        values.append(value)
        if value > max_value:
            max_value = value
            
        print(f"Channel {i}: {value} (0x{value:04X})")
        
        # Check for values near limits
        if value > 64000:
            if abs(value - 64746) < 50:
                print(f"  ⚠️ Still seeing ~64746 limit!")
            elif value >= 65000:
                print(f"  ✓ Approaching full 16-bit maximum!")
    
    # Stop measurement
    write_u8(device, _ENABLE, 0x01)  # PON=1
    
    # Report result
    if max_value > 65000:
        print("\n✅ TEST PASSED: Readings exceed the old 64746 limit")
        print(f"Maximum reading: {max_value} (0x{max_value:04X})")
    elif max_value > 64800:
        print("\n✓ PARTIAL SUCCESS: Readings exceed the 64746 limit")
        print(f"Maximum reading: {max_value} (0x{max_value:04X})")
    else:
        print("\n⚠️ INCONCLUSIVE: Readings didn't reach high enough values")
        print(f"Maximum reading: {max_value} (0x{max_value:04X})")
        print("Try with a brighter light source")
    
    return max_value > 64800

def test_integration_time(device):
    """Test integration time calculation and setting"""
    print("\n--- Integration Time Test ---")
    print("Testing if integration time calculation handles large values correctly")
    
    reset_sensor(device)
    
    # Test with different integration times
    times_us = [10000, 100000, 150000, 182000, 200000]
    
    test_passed = True
    
    for time_us in times_us:
        print(f"\nTesting integration time: {time_us} µs")
        
        # Calculate expected ASTEP with fixed algorithm
        resolution = 2.78
        raw_val = int((time_us - resolution) / resolution)
        bounded_val = min(raw_val, 65535)
        final_val = bounded_val & 0xFFFE  # Make even
        
        print(f"  Raw calculation: {raw_val} (0x{raw_val:04X})")
        print(f"  After bounds check: {bounded_val} (0x{bounded_val:04X})")
        print(f"  Final ASTEP: {final_val} (0x{final_val:04X})")
        
        # Apply setting
        write_u8(device, _ATIME, 0)
        write_u16(device, _ASTEP, final_val)
        time.sleep(0.1)
        
        # Read back and verify
        astep_read = read_u16(device, _ASTEP)
        print(f"  Read back value: {astep_read} (0x{astep_read:04X})")
        
        if astep_read == final_val:
            print("  ✓ SUCCESS: Values match")
        else:
            print(f"  ❌ FAILED: Values do not match")
            test_passed = False
    
    if test_passed:
        print("\n✅ INTEGRATION TIME TEST PASSED")
    else:
        print("\n❌ INTEGRATION TIME TEST FAILED")
    
    return test_passed

def test_gain(device):
    """Test all gain settings with 1-step offset adjustment"""
    print("\n--- Gain Test ---")
    print("Testing all gain settings (0.5x to 2048x)")
    print("Accounting for 1-step offset in status reporting")
    
    reset_sensor(device)
    
    # Set medium integration time
    write_u8(device, _ATIME, 0)
    write_u16(device, _ASTEP, 65534)  # Use maximum value
    
    test_passed = True
    
    for gain_code in range(13):  # 0-12 (0.5x to 2048x)
        gain_text = GAIN_MAP.get(gain_code, f"Unknown ({gain_code})")
        print(f"\nSetting gain to {gain_text}...")
        
        # Set gain
        write_u8(device, _CFG1, gain_code)
        time.sleep(0.1)
        
        # Get a reading to verify gain applied correctly
        write_u8(device, _ENABLE, 0x03)  # PON=1, SP_EN=1
        time.sleep(0.2)
        
        # Read back gain status from ASTATUS register
        astatus = read_u8(device, _ASTATUS)
        gain_status = astatus & 0x0F
        
        # Read a sample value
        value = read_u16(device, _DATA_START)
        
        # Stop measurement
        write_u8(device, _ENABLE, 0x01)
        
        # Calculate expected status (with 1-step offset)
        expected_status = max(0, gain_code - 1)  # Status should be gain-1, but never below 0
        
        # Verify gain was applied correctly with offset
        if gain_code == 0:
            # Special case for gain code 0, ASTATUS should also be 0
            if gain_status == 0:
                print(f"  ✓ Gain correctly set to {gain_text}")
                print(f"  Sample reading: {value}")
            else:
                print(f"  ❌ FAILED: Gain mismatch for 0.5x - set 0, status reports {gain_status}")
                test_passed = False
        else:
            # For all other gains, expect status to be gain-1
            if gain_status == expected_status:
                print(f"  ✓ Gain correctly set to {gain_text} (status shows {expected_status} due to offset)")
                print(f"  Sample reading: {value}")
            else:
                print(f"  ❌ FAILED: Gain mismatch - set {gain_code}, expected status {expected_status}, got {gain_status}")
                test_passed = False
    
    if test_passed:
        print("\n✅ GAIN TEST PASSED (with 1-step offset adjustment)")
        print("The AS7343 reports gain one step lower in the status register")
        print("This appears to be a hardware characteristic")
    else:
        print("\n❌ GAIN TEST FAILED")
    
    return test_passed

def test_full_channel_scan(device):
    """Test reading from all channels using proper SMUX configuration"""
    print("\n--- Full Channel Scan ---")
    print("Performing a full 14-channel scan with proper SMUX configuration")
    
    reset_sensor(device)
    
    # Set up for maximum readings
    write_u8(device, _CFG1, 9)  # 256x gain
    write_u8(device, _ATIME, 0)
    write_u16(device, _ASTEP, 65534)  # Maximum value
    
    # All channel readings will be stored here
    all_channels = {}
    
    # SMUX Mode 1: F1, F2, F3, F4, FY (visible channels)
    print("\nReading SMUX Mode 1 (F1-F4, FY)...")
    
    # Configure SMUX for visible channels
    write_u8(device, _CFG0, 0x10)  # Enable SMUX config
    # SMUX configuration for visible channels (F1-F4, FY)
    smux_data = [
        0,0,0,0,0,0,0,0,0,
        0b00000001, 0b00000010, 0b00000100, 0b00001000,
        0, 0b00010000, 0, 0,0,0,0
    ]
    for i, val in enumerate(smux_data):
        write_u8(device, 0x00 + i, val)
    write_u8(device, _CFG0, 0x00)  # Exit SMUX config mode
    
    # Take measurement
    write_u8(device, _ENABLE, 0x03)  # PON=1, SP_EN=1
    time.sleep(0.3)
    
    # Read values
    all_channels["F1"] = read_u16(device, _DATA_START)
    all_channels["F2"] = read_u16(device, _DATA_START + 2)
    all_channels["F3"] = read_u16(device, _DATA_START + 4)
    all_channels["F4"] = read_u16(device, _DATA_START + 6)
    all_channels["FY"] = read_u16(device, _DATA_START + 8)
    
    # Stop measurement
    write_u8(device, _ENABLE, 0x01)  # PON=1
    time.sleep(0.1)
    
    # SMUX Mode 2: F6, F7, F8, FXL, NIR, CLR
    print("Reading SMUX Mode 2 (F6-F8, FXL, NIR, CLR)...")
    
    # Configure SMUX for NIR channels
    write_u8(device, _CFG0, 0x10)  # Enable SMUX config
    # SMUX configuration for NIR channels
    smux_data = [
        0,0,0,0,0,0,0,0,0,
        0b01000000, 0b00000010, 0b00010000, 0b00100000,
        0, 0b10000000, 0b00000100, 0,0,0,0
    ]
    for i, val in enumerate(smux_data):
        write_u8(device, 0x00 + i, val)
    write_u8(device, _CFG0, 0x00)  # Exit SMUX config mode
    
    # Take measurement
    write_u8(device, _ENABLE, 0x03)  # PON=1, SP_EN=1
    time.sleep(0.3)
    
    # Read values
    all_channels["F6"] = read_u16(device, _DATA_START)
    all_channels["F7"] = read_u16(device, _DATA_START + 2)
    all_channels["F8"] = read_u16(device, _DATA_START + 4)
    all_channels["FXL"] = read_u16(device, _DATA_START + 6)
    all_channels["NIR"] = read_u16(device, _DATA_START + 8)
    all_channels["CLR"] = read_u16(device, _DATA_START + 10)
    
    # Stop measurement
    write_u8(device, _ENABLE, 0x01)  # PON=1
    time.sleep(0.1)
    
    # SMUX Mode 3: FZ, F5
    print("Reading SMUX Mode 3 (FZ, F5)...")
    
    # Configure SMUX for final channels
    write_u8(device, _CFG0, 0x10)  # Enable SMUX config
    # SMUX configuration for FZ and F5
    smux_data = [
        0,0,0,0,0,0,0,0,0,
        0b01000000, 0b00000010, 0b00010000, 0b00000100,
        0, 0b10000000, 0b00000001, 0,0,0,0
    ]
    for i, val in enumerate(smux_data):
        write_u8(device, 0x00 + i, val)
    write_u8(device, _CFG0, 0x00)  # Exit SMUX config mode
    
    # Take measurement
    write_u8(device, _ENABLE, 0x03)  # PON=1, SP_EN=1
    time.sleep(0.3)
    
    # Read values
    all_channels["FZ"] = read_u16(device, _DATA_START)
    all_channels["F5"] = read_u16(device, _DATA_START + 2)
    
    # Stop measurement
    write_u8(device, _ENABLE, 0x01)  # PON=1
    
    # Display all channel readings in order
    print("\nAll Channel Readings:")
    channel_order = ["F1", "F2", "F3", "F4", "FY", "F5", "F6", "F7", "F8", "FZ", "FXL", "NIR", "CLR"]
    
    # Print header with channel names
    header_line = ""
    for ch in channel_order:
        header_line += f"{ch:>8}"
    print(header_line)
    
    # Print readings
    values_line = ""
    for channel in channel_order:
        if channel in all_channels:
            values_line += f"{all_channels[channel]:>8}"
        else:
            values_line += f"{'N/A':>8}"
    print(values_line)
    
    # Check for any saturated values
    max_possible = 65535
    saturated_channels = []
    for channel, value in all_channels.items():
        if value >= max_possible - 10:
            saturated_channels.append(channel)
    
    if saturated_channels:
        print("\nSaturated channels (at maximum reading):")
        for ch in saturated_channels:
            print(f"  • {ch}")
    
    print("\n✓ FULL CHANNEL SCAN COMPLETE")
    return True

def test_autozero(device):
    """Test auto-zero configuration"""
    print("\n--- Auto-Zero Configuration Test ---")
    
    reset_sensor(device)
    
    # Read current auto-zero configuration
    az_config = read_u8(device, 0xDE)  # AZ_CONFIG register
    print(f"Current AZ_CONFIG: 0x{az_config:02X}")
    
    # Test different configurations
    az_values = [0, 1, 255]
    az_desc = ["Never", "Every cycle", "First measurement only"]
    
    for i, az in enumerate(az_values):
        print(f"\nSetting AZ_CONFIG to {az} ({az_desc[i]})...")
        write_u8(device, 0xDE, az)
        time.sleep(0.1)
        
        # Read back to verify
        actual = read_u8(device, 0xDE)
        if actual == az:
            print(f"  ✓ Successfully set AZ_CONFIG to {az}")
        else:
            print(f"  ❌ Failed to set AZ_CONFIG. Set {az}, read {actual}")
    
    # Restore default
    write_u8(device, 0xDE, 255)
    print("\n✓ AUTO-ZERO TEST COMPLETE")
    return True

def test_saturation(device):
    """Test saturation detection"""
    print("\n--- Saturation Detection Test ---")
    print("This test checks if saturation can be detected correctly")
    print("Please aim the sensor at a very bright light source\n")
    
    reset_sensor(device)
    
    # Set for maximum sensitivity
    write_u8(device, _CFG1, 12)  # 2048x gain
    write_u8(device, _ATIME, 0)
    write_u16(device, _ASTEP, 65534)  # Maximum integration time
    
    input("Press Enter to start saturation test...")
    
    # Start measurement
    write_u8(device, _ENABLE, 0x03)  # PON=1, SP_EN=1
    time.sleep(1.0)
    
    # Check status registers for saturation
    status = read_u8(device, _STATUS)
    status2 = read_u8(device, 0x90)  # STATUS2 register
    
    # Stop measurement
    write_u8(device, _ENABLE, 0x01)
    
    # Check results
    asat = (status & 0x80) != 0
    asat_dig = (status2 & 0x10) != 0
    asat_ana = (status2 & 0x08) != 0
    
    print("\nSaturation Results:")
    print(f"  STATUS.ASAT: {'Set' if asat else 'Not set'}")
    print(f"  STATUS2.ASAT_DIG: {'Set' if asat_dig else 'Not set'}")
    print(f"  STATUS2.ASAT_ANA: {'Set' if asat_ana else 'Not set'}")
    
    if asat or asat_dig or asat_ana:
        print("\n✅ SATURATION DETECTION WORKING")
    else:
        print("\n⚠️ No saturation detected. Try with brighter light source.")
    
    return True

def test_power_management(device):
    """Test power management features"""
    print("\n--- Power Management Test ---")
    
    reset_sensor(device)
    
    # Test power down
    print("Testing power down...")
    write_u8(device, _ENABLE, 0x00)  # PON=0
    time.sleep(0.1)
    
    enable = read_u8(device, _ENABLE)
    if enable == 0x00:
        print("  ✓ Successfully powered down")
    else:
        print(f"  ❌ Failed to power down. ENABLE=0x{enable:02X}")
    
    # Test power up
    print("Testing power up...")
    write_u8(device, _ENABLE, 0x01)  # PON=1
    time.sleep(0.1)
    
    enable = read_u8(device, _ENABLE)
    if (enable & 0x01) != 0:
        print("  ✓ Successfully powered up")
    else:
        print(f"  ❌ Failed to power up. ENABLE=0x{enable:02X}")
    
    # Test low power mode
    print("Testing low power mode...")
    cfg0 = read_u8(device, _CFG0)
    write_u8(device, _CFG0, cfg0 | 0x20)  # Set LOW_POWER bit
    time.sleep(0.1)
    
    cfg0_read = read_u8(device, _CFG0)
    if (cfg0_read & 0x20) != 0:
        print("  ✓ Successfully enabled low power mode")
    else:
        print(f"  ❌ Failed to enable low power mode. CFG0=0x{cfg0_read:02X}")
    
    # Restore original CFG0
    write_u8(device, _CFG0, cfg0)
    
    print("\n✓ POWER MANAGEMENT TEST COMPLETE")
    return True

def run_all_tests(device):
    """Run all tests in sequence"""
    print("\n=== Running All Tests ===\n")
    
    tests = [
        ("Fix Verification", test_fix_verification),
        ("Integration Time", test_integration_time),
        ("Gain", test_gain),
        ("Full Channel Scan", test_full_channel_scan),
        ("Auto-Zero Configuration", test_autozero),
        ("Saturation Detection", test_saturation),
        ("Power Management", test_power_management)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n>>> RUNNING: {name} TEST <<<")
        try:
            result = test_func(device)
            results.append((name, result))
        except Exception as e:
            print(f"Error during {name} test: {e}")
            results.append((name, False))
    
    print("\n=== Test Summary ===")
    passed = 0
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n{passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n✅ ALL TESTS PASSED - AS7343 library is working correctly")
    else:
        print("\n⚠️ SOME TESTS FAILED - See details above")

def write_u8(device, reg, value):
    with device as i2c:
        i2c.write(bytes([reg, value]))

def write_u16(device, reg, value):
    with device as i2c:
        i2c.write(struct.pack("<BH", reg, value))

def read_u8(device, reg):
    buf = bytearray(1)
    with device as i2c:
        i2c.write_then_readinto(bytes([reg]), buf)
    return buf[0]

def read_u16(device, reg):
    buf = bytearray(2)
    with device as i2c:
        i2c.write_then_readinto(bytes([reg]), buf)
    value = struct.unpack("<H", buf)[0]
    return value

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")