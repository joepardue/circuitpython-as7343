# as7343.py - Minimal CircuitPython driver for AS7343 sensor
import time
import struct
import adafruit_bus_device.i2c_device as i2c_device

AS7343_DEFAULT_ADDRESS = 0x39

class AS7343:
    def __init__(self, i2c):
        self.i2c_device = i2c_device.I2CDevice(i2c, AS7343_DEFAULT_ADDRESS)
        self._soft_reset()
        if not self._verify_sensor():
            raise RuntimeError("AS7343 not detected on I2C bus!")
        self._configure_sensor()

    def _soft_reset(self):
        self._write_register(0x80, 0x10)
        time.sleep(0.1)

    def _verify_sensor(self):
        try:
            status2 = self._read_register(0xA3)
            return (status2 & 0x10) == 0x10
        except:
            return False

    def _configure_sensor(self):
        # Setup Auto SMUX, FIFO, ENABLE
        self._write_register(0x80, 0x01)  # PON
        self._write_register(0x81, 0x02)  # SMUX command
        time.sleep(0.1)

    def data_ready(self):
        status3 = self._read_register(0xA4)
        return (status3 & 0x80) != 0

    def read_fifo(self):
        data = bytearray(12)
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytes([0xFC]), data)
        readings = struct.unpack_from(">6H", data)
        return readings

    def _read_register(self, reg):
        buf = bytearray(1)
        with self.i2c_device as i2c:
            i2c.write_then_readinto(bytes([reg]), buf)
        return buf[0]

    def _write_register(self, reg, value):
        with self.i2c_device as i2c:
            i2c.write(bytes([reg, value]))
