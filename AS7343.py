# SPDX-FileCopyrightText: 2025 Your Name
#
# SPDX-License-Identifier: MIT

"""
`as7343`
================================================================================

CircuitPython driver for the AMS AS7343 14-channel spectral sensor, which provides
high-resolution spectral measurements across the visible and near-infrared spectrum.

* Author(s): Your Name

Implementation Notes
--------------------

**Hardware:**

* `AMS AS7343 14-Channel Spectral Sensor <https://ams.com/as7343>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

import time
import struct
from adafruit_bus_device.i2c_device import I2CDevice

__version__ = "0.0.1"
__repo__ = "https://github.com/your_username/CircuitPython_AS7343.git"

# I2C Address
_AS7343_I2C_ADDR = 0x39

# Register addresses
_ENABLE = 0x80
_ATIME = 0x81
_WTIME = 0x83
_ASTEP = 0xD4
_CFG0 = 0xBF
_CFG1 = 0xC6
_CFG3 = 0xC7
_CFG20 = 0xD6
_CONTROL = 0xFA
_STATUS4 = 0xBC
_DATA_START = 0x95
_ASTATUS = 0x94

# Enable flags
_ENABLE_PON = 0x01  # Power ON
_ENABLE_SP_EN = 0x02  # Spectral Measurement Enable
_ENABLE_WEN = 0x08  # Wait Enable
_CONTROL_SW_RESET = 0x08  # Software Reset

# Low power and interrupt flags
_LOW_POWER_BIT = 0x20  # Bit 5 in CFG0
_SAI_BIT = 0x10        # Bit 4 in CFG3 (Sleep After Interrupt)
_CLEAR_SAI_ACT = 0x01  # Bit 0 in CONTROL
_SAI_ACTIVE = 0x02     # Bit 1 in STATUS4

# Gain values
GAIN_0_5X = 0x00   #: 0.5x gain setting
GAIN_1X = 0x01     #: 1x gain setting
GAIN_2X = 0x02     #: 2x gain setting
GAIN_4X = 0x03     #: 4x gain setting
GAIN_8X = 0x04     #: 8x gain setting
GAIN_16X = 0x05    #: 16x gain setting
GAIN_32X = 0x06    #: 32x gain setting
GAIN_64X = 0x07    #: 64x gain setting
GAIN_128X = 0x08   #: 128x gain setting
GAIN_256X = 0x09   #: 256x gain setting
GAIN_512X = 0x0A   #: 512x gain setting
GAIN_1024X = 0x0B  #: 1024x gain setting
GAIN_2048X = 0x0C  #: 2048x gain setting

# SMUX mode identifiers
SMUX_VISIBLE = "VISIBLE"  #: SMUX configuration for visible light channels (F1-F4, FY)
SMUX_NIR = "NIR"          #: SMUX configuration for NIR channels (F6-F8, FXL, NIR, CLR)
SMUX_FZF5 = "FZF5"        #: SMUX configuration for additional channels (FZ, F5)


class AS7343:
    """
    Driver for the AMS AS7343 14-channel spectral sensor.

    This sensor provides high-resolution spectral measurements across the visible
    and near-infrared spectrum with 14 distinct channels (F1-F8, FZ, FY, FXL, NIR, CLR).

    :param ~busio.I2C i2c: The I2C bus the AS7343 is connected to
    """

    def __init__(self, i2c):
        """
        Initialize the AS7343 sensor.

        :param ~busio.I2C i2c: The I2C bus the AS7343 is connected to
        """
        self.i2c_device = I2CDevice(i2c, _AS7343_I2C_ADDR)
        self._smux_modes = self._define_smux_modes()
        self._last_data = {}
        self._gain = None
        self._integration_time_us = None
        self.initialize()
        self.gain = GAIN_4X
        self.integration_time = 150000

    def initialize(self):
        """
        Perform a software reset and basic startup configuration.
        
        Resets the device to its default state and prepares it for measurements.
        """
        self._write_u8(_CONTROL, _CONTROL_SW_RESET)
        time.sleep(1.0)
        self._write_u8(_CFG0, 0x00)
        self._write_u8(_WTIME, 0x00)

    @property
    def gain(self):
        """
        The ADC gain setting for the sensor.
        
        This setting controls the amplification of the sensor signal before it
        is converted to a digital value. Higher gain values allow detection of
        dimmer light sources, but may cause saturation with bright sources.
        
        :return: Current gain setting (one of the GAIN_* constants)
        """
        return self._gain

    @gain.setter
    def gain(self, value):
        """
        Set the ADC gain for the sensor.
        
        :param value: One of the GAIN_* constants (0x00-0x0C)
        :raises ValueError: If an invalid gain value is provided
        """
        if value not in range(0x00, 0x0D):
            raise ValueError("Invalid gain setting.")
        self._write_u8(_CFG1, value)
        self._gain = value

    @property
    def integration_time(self):
        """
        The integration time in microseconds.
        
        This controls how long the sensor collects light for each measurement.
        Longer integration times provide better results in low light but may
        cause saturation in bright conditions.
        
        :return: Integration time in microseconds
        """
        return self._integration_time_us

    @integration_time.setter
    def integration_time(self, integration_time_us):
        """
        Set the integration time for spectral measurements.
        
        :param integration_time_us: Desired integration time in microseconds
        :raises ValueError: If integration time is too long
        """
        resolution = 2.78
        if integration_time_us > (65535 * resolution):
            raise ValueError("Integration time too long.")
        
        # Calculate ASTEP with bounds checking
        astep_value = int((integration_time_us - resolution) / resolution)
        astep_value = min(astep_value, 65535)
        astep_value = astep_value & 0xFFFE
        
        self._write_u8(_ATIME, 0)
        self._write_u16(_ASTEP, astep_value)
        self._integration_time_us = integration_time_us
        
    def set_smux_mode(self, mode_name):
        """
        Apply a predefined SMUX (sensor multiplexer) configuration.
        
        The AS7343 has more channels than ADCs, so channel mapping is controlled
        by the SMUX configuration. This method configures a specific channel set.
        
        :param mode_name: One of the SMUX_* constants
        :raises ValueError: If an invalid mode name is provided
        """
        if mode_name not in self._smux_modes:
            raise ValueError(f"Invalid SMUX mode: {mode_name}")
        config = self._smux_modes[mode_name]["smux"]
        self._write_u8(_CFG0, 0x10)  # Enable SMUX config mode
        for i, val in enumerate(config):
            self._write_u8(0x00 + i, val)
        self._write_u8(_CFG0, 0x00)  # Exit SMUX config mode

    def get_smux_map(self, mode_name):
        """
        Get the channel mapping for a specific SMUX mode.
        
        :param mode_name: One of the SMUX_* constants
        :return: List of (label, register_address) tuples
        :raises ValueError: If an invalid mode name is provided
        """
        if mode_name not in self._smux_modes:
            raise ValueError(f"Invalid SMUX mode: {mode_name}")
        return self._smux_modes[mode_name]["map"]

    def read_all(self):
        """
        Perform a complete scan of all 14 spectral channels.
        
        This method takes three separate measurements with different SMUX
        configurations to read all channels, and combines the results.
        
        :return: Dictionary with channel labels (F1, F2, etc.) mapping to values
        """
        full_data = {}
        for mode_name in self._smux_modes:
            self.set_smux_mode(mode_name)
            label_map = self._smux_modes[mode_name]["map"]
            self.start_measurement()
            time.sleep(0.5)
            self.stop_measurement()
            for label, reg in label_map:
                full_data[label] = self._read_u16(reg)
        self._last_data = full_data
        return full_data

    @property
    def data(self):
        """
        The most recent spectral measurement data.
        
        :return: Dictionary mapping channel labels to values
        """
        return self._last_data

    @property
    def channels(self):
        """
        All spectral channel values in a standard order.
        
        :return: List of values in the order: F1, F2, F3, F4, FY, F5, F6, F7, F8, FZ, FXL, NIR, CLR
        """
        labels = ["F1", "F2", "F3", "F4", "FY", "F5", "F6", "F7", "F8", "FZ", "FXL", "NIR", "CLR"]
        return [self._last_data.get(label, 0) for label in labels]

    def _define_smux_modes(self):
        """
        Define the SMUX configurations for all channel groups.
        
        :return: Dictionary of SMUX mode configurations
        """
        return {
            SMUX_VISIBLE: {
                "smux": [0,0,0,0,0,0,0,0,0,0x01,0x02,0x04,0x08,0,0x10,0,0,0,0,0],
                "map": [("F1", 0x95), ("F2", 0x97), ("F3", 0x99), ("F4", 0x9B), ("FY", 0x9D)]
            },
            SMUX_NIR: {
                "smux": [0,0,0,0,0,0,0,0,0,0x40,0x02,0x10,0x20,0,0x80,0x04,0,0,0,0],
                "map": [("F6", 0x95), ("F7", 0x97), ("F8", 0x99), ("FXL", 0x9B), ("NIR", 0x9D), ("CLR", 0x9F)]
            },
            SMUX_FZF5: {
                "smux": [0,0,0,0,0,0,0,0,0,0x40,0x02,0x10,0x04,0,0x80,0x01,0,0,0,0],
                "map": [("FZ", 0x95), ("F5", 0x97)]
            }
        }

    def start_measurement(self):
        """
        Begin a spectral measurement.
        
        This starts the sensor integration. Call stop_measurement() after an
        appropriate delay to complete the measurement.
        """
        self._write_u8(_ENABLE, _ENABLE_WEN | _ENABLE_SP_EN | _ENABLE_PON)

    def stop_measurement(self):
        """
        End a spectral measurement.
        
        This stops sensor integration and makes the data available for reading.
        """
        self._write_u8(_ENABLE, _ENABLE_PON)

    def read_smux_mode(self, mode_name):
        """
        Read only the channels defined in one SMUX mode.
        
        This is more efficient than read_all() when only specific channels are needed.
        
        :param mode_name: One of the SMUX_* constants
        :return: Dictionary of channel labels mapping to values
        """
        self.set_smux_mode(mode_name)
        mapping = self.get_smux_map(mode_name)
        self.start_measurement()
        time.sleep(0.25)
        self.stop_measurement()
        return {label: self._read_u16(reg) for label, reg in mapping}

    def enable_low_power_mode(self, enable=True):
        """
        Enable or disable low power mode.
        
        In low power mode, the device consumes less power when idle.
        
        :param enable: True to enable, False to disable low power mode
        """
        cfg0 = self._read_u8(_CFG0)
        cfg0 |= _LOW_POWER_BIT if enable else cfg0 & ~_LOW_POWER_BIT
        self._write_u8(_CFG0, cfg0)

    def enable_sleep_after_interrupt(self, enable=True):
        """
        Enable or disable Sleep After Interrupt (SAI) mode.
        
        In SAI mode, the device enters sleep state when an interrupt occurs.
        
        :param enable: True to enable, False to disable SAI
        """
        cfg3 = self._read_u8(_CFG3)
        cfg3 |= _SAI_BIT if enable else cfg3 & ~_SAI_BIT
        self._write_u8(_CFG3, cfg3)

    def clear_sleep_active(self):
        """Clear the Sleep After Interrupt active status."""
        self._write_u8(_CONTROL, _CLEAR_SAI_ACT)

    def is_device_sleeping(self):
        """
        Check if the device is in sleep mode.
        
        :return: True if sleeping, False otherwise
        """
        return (self._read_u8(_STATUS4) & _SAI_ACTIVE) != 0

    def shutdown(self):
        """
        Power down the device.
        
        This puts the device in the lowest power consumption state.
        """
        self._write_u8(_ENABLE, 0x00)

    def wake(self):
        """
        Wake up the device from shutdown.
        
        This restores power to the device but does not start measurements.
        """
        self._write_u8(_ENABLE, _ENABLE_PON)
        time.sleep(0.01)
        
    def check_thresholds(self, threshold, data=None):
        """
        Return a list of channels that exceed a given threshold.
        
        :param threshold: Warning threshold value (int)
        :param data: Optional dictionary of channel readings (default: self.data)
        :return: List of (label, value) pairs where value >= threshold
        """
        if data is None:
            data = self.data

        flagged = []
        for label, val in data.items():
            if not isinstance(val, int):
                print(f"⚠️ TypeError: {label} = {val} (type: {type(val)}) — expected int")
                continue
            if val >= threshold:
                flagged.append((label, val))
        return flagged

    # ------------------------------------------------
    # Low-level register I/O methods
    # ------------------------------------------------
    
    def _read_u8(self, reg):
        """Read an 8-bit unsigned value from the specified register."""
        buf = bytearray(1)
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytes([reg]), buf)
        return buf[0]

    def _write_u8(self, reg, value):
        """Write an 8-bit unsigned value to the specified register."""
        with self.i2c_device as i2c:
            i2c.write(bytes([reg, value]))

    def _read_u16(self, reg):
        """Read a 16-bit little-endian unsigned value from the specified register."""
        buf = bytearray(2)
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytes([reg]), buf)
        return struct.unpack("<H", buf)[0]

    def _write_u16(self, reg, value):
        """Write a 16-bit little-endian unsigned value to the specified register."""
        with self.i2c_device as i2c:
            i2c.write(struct.pack("<BH", reg, value))