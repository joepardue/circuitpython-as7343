AS7343 CircuitPython Library
=============================

7/23/25 - I just came across the newly released SparkFun library for the AS7343. Comparisons* are shown at the end of this README.md. TL;DR: Use this library for CircuitPython-only projects that need advanced sensor control; use SparkFun's for cross-platform compatibility across Python/MicroPython/CircuitPython.

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

Features
--------

- Full 14-channel spectral measurement using read_all()
- SMUX mode selection for visible, NIR, and extended bands
- Low-power mode and sleep-after-interrupt (SAI)
- Saturation threshold checking
- Compatible with CircuitPython and Adafruit BusDevice

Installation
------------

1. Download the CircuitPython library bundle from https://circuitpython.org/libraries
2. Copy the following into the `lib/` directory on your device:
   - `as7343.py` (from this repo)
   - `adafruit_bus_device` (from the bundle)

Usage Example
-------------

.. code-block:: python

    import board
    import as7343
    import time

    i2c = board.STEMMA_I2C()
    sensor = as7343.AS7343(i2c)
    sensor.gain = as7343.GAIN_64X
    sensor.integration_time = 100000

    data = sensor.read_all()
    for ch, val in data.items():
        print(f"{ch}: {val}")

Advanced Use
------------

SMUX Read Example::

    sensor.read_smux_mode(as7343.SMUX_VISIBLE)
    sensor.read_smux_mode(as7343.SMUX_NIR)
    sensor.read_smux_mode(as7343.SMUX_FZF5)

Power Management::

    sensor.enable_low_power_mode(True)
    sensor.enable_sleep_after_interrupt(True)
    sensor.shutdown()
    sensor.wake()

Threshold Check::

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

## Included in the CircuitPython Community Bundle 🌟

This `circuitpython-as7343` library has been officially accepted into the
[CircuitPython Community Library Bundle](https://github.com/adafruit/CircuitPython_Community_Bundle).

This means it has undergone review by the CircuitPython team and community maintainers
to ensure it meets quality and compatibility standards.

You can find it listed in the [Python on Microcontrollers Newsletter (May 20, 2025)](https://blog.adafruit.com/2025/05/20/icymi-python-on-microcontrollers-newsletter-python-jumps-in-popularity-hacking-pis-new-circuitpython-and-more-circuitpython-python-micropython-raspberry_pi/)
under "New CircuitPython Libraries."

To easily use this library, it's recommended to download the full bundle from
[circuitpython.org/libraries](https://circuitpython.org/libraries).

*Comparison with SparkFun AS7343 Library
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

License
-------

MIT License

Author
------

Joe Pardue https://github.com/joepardue/AS7343-circuitpython-bundle
