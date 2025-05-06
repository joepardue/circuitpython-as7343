AS7343 CircuitPython Starter Bundle

Files included:
- as7343.py : Minimal driver for AS7343 using Auto-SMUX and FIFO reading
- code.py   : Simple test program that waits for 'g' input and prints channel data

Summary:
- Sensor soft reset at startup
- Sensor verified (STATUS2 read)
- Auto SMUX setup
- FIFO reading used for efficient capture
- Terminal prints readings cleanly one per line

Future goals:
- Improve output formatting
- Add automatic gain adjustment
- Add CSV logging

Ready for fresh development!
