AS7343 CircuitPython Library
=============================

*7/23/25 - I just came across the newly released SparkFun library for the AS7343. Comparisons are shown at the end of this README.md. TL;DR: Use this library for CircuitPython-only projects that need advanced sensor control or if you prefer to work with adafruit; use sparkfun's for cross-platform compatibility across Python/MicroPython/CircuitPython or if you prefer to work with sparkfun.*

*7/25/25 This code is all tested with the Pimoroni I2C AS7343 breakout board since Adafruit does not, at present, have on. It works well withing the Adafruit CircuitPython ecosystem and may be viewed at:
https://shop.pimoroni.com/products/as7343-breakout?variant=41694602526803* 

A CircuitPython driver for the AMS AS7343 14-channel spectral sensor. This device provides high-resolution spectral measurements across the visible and near-infrared spectrum, making it ideal for:

- Color measurement and classification
- LED spectrum analysis
- Environmental light sensing
- Low-cost lab and educational tools

Description
-----------

The AMS AS7343 is a spectral sensor offering readings from approximately 380nm to 1000nm. It includes:

- 14 photodiode channels: F1–F8, FZ, FY, FXL, NIR, and CLR
- Adjustable gain (0.5x to 2048x)
- Integration time in microseconds
- Internal SMUX (sensor multiplexer) to cycle through photodiode sets
- I2C interface (address 0x39)

This driver provides methods to set gain/integration time, select SMUX modes, perform full or partial scans, and manage power settings.

**Note about Channel Sensitivity:** Some channels (particularly F3, F4, F8, and FXL) naturally produce significantly lower values due to their specific spectral sensitivity characteristics. This is expected hardware behavior, not a software error. See the AS7343 datasheet Figure 8 for detailed spectral response curves showing the varying sensitivity across channels.

Features
--------

- Full 14-channel spectral measurement using read_all()
- Property-based API (sensor.gain = GAIN_64X, sensor.integration_time = 100000)
- SMUX mode selection for visible, NIR, and extended bands
- Complete gain constants (GAIN_0_5X through GAIN_2048X)
- Low-power mode and sleep-after-interrupt (SAI) functionality
- Saturation threshold checking
- Compatible with CircuitPython and Adafruit BusDevice

Installation
------------

1. Download the CircuitPython library bundle from https://circuitpython.org/libraries
2. Copy the following into the `lib/` directory on your device:
   - `as7343/__init__.py` (from this repo)
   - `adafruit_bus_device` (from the bundle)

Usage Example
-------------

.. code-block:: python

    import board
    import as7343
    import time

    i2c = board.STEMMA_I2C()
    sensor = as7343.AS7343(i2c)
    
    # Set measurement parameters using property API
    sensor.gain = as7343.GAIN_64X
    sensor.integration_time = 100000

    # Read all 14 spectral channels
    data = sensor.read_all()
    for ch, val in data.items():
        print(f"{ch}: {val}")

    # Access ordered channel data
    channels = sensor.channels  # Returns list in standard order
    print(f"F1 value: {channels[0]}")

Advanced Use
------------

SMUX Mode Control::

    # Read specific channel groups
    visible_data = sensor.read_smux_mode(as7343.SMUX_VISIBLE)  # F1-F4, FY
    nir_data = sensor.read_smux_mode(as7343.SMUX_NIR)          # F6-F8, FXL, NIR, CLR
    extended_data = sensor.read_smux_mode(as7343.SMUX_FZF5)    # FZ, F5

Power Management::

    sensor.enable_low_power_mode(True)
    sensor.enable_sleep_after_interrupt(True)
    sensor.clear_sleep_active()
    sensor.shutdown()
    sensor.wake()

Threshold Checking::

    # Check for saturation or minimum light levels
    alerts = sensor.check_thresholds(60000)
    for ch, value in alerts:
        print(f"High reading: {ch} = {value}")

Supported Channels
------------------

- F1, F2, F3, F4 – Violet to green (405–515 nm)
- FY, F5 – Green/yellow (~555–560 nm)  
- F6, F7, F8 – Red to deep red (640–745 nm)
- FZ, FXL – Additional narrowbands (450, 600 nm)
- NIR – Near infrared (~855 nm)
- CLR – Clear (broadband)

**Note:** F3, F4, F8, and FXL channels typically show lower values due to their specific spectral sensitivity. This is normal hardware behavior - see AS7343 datasheet Figure 8 for spectral response details.

Testing the Driver
------------------

The library includes comprehensive test modules for validating functionality. Copy any of these to `code.py` to test specific features:

**examples/as7343_test_basic.py** - Tests initialization, property API, and basic functionality::

    # Tests gain/integration time properties, power management basics
    # Expected: All PASS results for property setting/getting

**examples/as7343_test_SMUX.py** - Tests sensor multiplexer functionality::

    # Tests SMUX mode switching, channel mapping, error handling  
    # Expected: Proper channel counts per mode (VISIBLE: 5, NIR: 6, FZF5: 2)

**examples/as7343_test_measurement.py** - Tests full spectral measurement system::

    # Tests read_all(), data/channels properties, timing, repeatability
    # Expected: 13 channels, ~1.5 second measurement time, stable readings

**examples/as7343_test_power.py** - Tests power management features::

    # Tests shutdown/wake cycles, low power mode, SAI functionality
    # Expected: Robust power cycling, no measurement failures

**examples/as7343_test_thresholds.py** - Tests threshold detection::

    # Tests check_thresholds(), saturation detection, error handling
    # Expected: Proper threshold flagging, graceful error handling

Run these tests in sequence to verify complete driver functionality. All tests should show mostly PASS results.

Advanced Features Available Separately
--------------------------------------

For applications requiring temperature compensation, auto-ranging, or advanced calibration features, see `as7343_temperature.py` which provides:

- **auto_range_optimal()** - Automatically determines optimal gain and integration time settings
- **is_saturated()** / **get_saturated_channels()** - Saturation detection and handling  
- **get_basic_counts()** - Normalizes raw ADC values for cross-setting comparison
- **Temperature compensation** - Corrects readings based on calibration coefficients
- **Calibration data management** - Stores and applies correction factors

These advanced features are maintained separately to keep the core driver focused and lightweight.

Included in the CircuitPython Community Bundle 🌟
-------------------------------------------------
This `circuitpython-as7343` library has been officially accepted into the
[CircuitPython Community Library Bundle](https://github.com/adafruit/CircuitPython_Community_Bundle).

This means it has undergone review by the CircuitPython team and community maintainers
to ensure it meets quality and compatibility standards.

You can find it listed in the [Python on Microcontrollers Newsletter (May 20, 2025)](https://blog.adafruit.com/2025/05/20/icymi-python-on-microcontrollers-newsletter-python-jumps-in-popularity-hacking-pis-new-circuitpython-and-more-circuitpython-python-micropython-raspberry_pi/)
under "New CircuitPython Libraries."

To easily use this library, it's recommended to download the full bundle from
[circuitpython.org/libraries](https://circuitpython.org/libraries).

Comparison with SparkFun AS7343 Library
---------------------------------------
Use this library if you:

Are building CircuitPython projects with other Adafruit sensors
Want advanced features like SMUX mode control and power management
Prefer native CircuitPython integration and performance

Use SparkFun's library if you:

Need to run the same code across Python/MicroPython/CircuitPython platforms
Want access to all data registers and measurement cycles
Are already using other SparkFun Qwiic sensors

Key Differences:

Platform Support: This library is CircuitPython-only; SparkFun's works across multiple Python variants
Integration: Uses adafruit_bus_device; SparkFun's uses their qwiic_i2c abstraction
API Focus: This library emphasizes the 14 distinct sensor channels; SparkFun's exposes lower-level register access

Both are well-maintained. Choose based on your platform requirements and feature needs.

IMPORTANT NOTE:
---------------
Some folks on the Internet have tried to fix the problem of F3 and F8 indicating counts at ~25% of the rest of the channels. This isn't actually a problem, but inherent in those channels as shown in Figure 8 of the datasheet: https://look.ams-osram.com/m/5f2d27fff9a874d2/original/AS7343-14-Channel-Multi-Spectral-Sensor.pdf

License
-------

MIT License

Author
------

Joe Pardue https://github.com/joepardue/AS7343-circuitpython-bundle
EOF
