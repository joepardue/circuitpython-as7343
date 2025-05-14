Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-as7343/badge/?version=latest
    :target: https://adafruit-circuitpython-as7343.readthedocs.io/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/joepardue/circuitpython-as7343/workflows/Build%20CI/badge.svg
    :target: https://github.com/joepardue/circuitpython-as7343/actions
    :alt: Build Status

CircuitPython driver for the AS7343 spectral sensor


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Usage Example
=============

.. code-block:: python

    import board
    import adafruit_as7343

    i2c = board.I2C()
    sensor = adafruit_as7343.AS7343(i2c)
    
    # Example usage code here
