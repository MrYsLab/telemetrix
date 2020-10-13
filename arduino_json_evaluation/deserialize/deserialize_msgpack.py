import json
import msgpack
import serial
import sys
import time
from collections import deque

# Sketch uses 3576 bytes (11%) of program storage space. Maximum is 32256 bytes.
# Global variables use 567 bytes (27%) of dynamic memory, leaving 1481 bytes for local variables. Maximum is 2048 bytes.


class JsonDeserialize:
    def __init__(self):
        self.serial_port = serial.Serial('/dev/ttyACM0', 115200,
                                         timeout=1, writeTimeout=0)
        self.start_time = 0
        self.end_time = 0

        print('open')
        count = 0

        length = 0
        while True:
            # try:
            if self.serial_port.inWaiting():
                # the first byte retrieved is the length of the packet
                length = int.from_bytes(self.serial_port.read(), "big")
                packet = self.serial_port.read(length)
                t = msgpack.unpackb(packet, raw=False)
                if t['count'] == 0:
                    self.start_time = time.time()

                if t["count"] == 999:
                    print(f'Elapsed time: {time.time() - self.start_time}')
                    sys.exit(0)
            else:
                try:
                    time.sleep(.000001)
                except KeyboardInterrupt:
                    sys.exit(0)

JsonDeserialize()
