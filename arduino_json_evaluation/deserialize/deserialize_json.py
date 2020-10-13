import json
import serial
import sys
import time


class JsonDeserialize:
    """
    Deserialize data from ArduinoJson.
    1000 packets will be sent. Show the time for the
    all the packets to be received and deserialized.

    Elapsed time = 8.813957691192627
    
    """

    def __init__(self):
        self.serial_port = serial.Serial('/dev/ttyACM0', 115200,
                                         timeout=1, writeTimeout=0)
        self.serial_port.reset_output_buffer()
        self.serial_port.reset_input_buffer()

        # Time that data started to arrive
        self.start_time = 0
        print('open')

        while True:
            try:
                if self.serial_port.inWaiting():
                    c = self.serial_port.read_until(b'}')
                    try:
                        b = json.loads(c)
                    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                        continue

                    # Save the start time when the first packet arrives
                    if b['count'] == 0:
                        self.start_time = time.time()

                    # calculate elapsed time when the last packet arrives
                    if b['count'] >= 999:
                        print(f'Elapsed time = {time.time() - self.start_time}')
                        sys.exit(0)
                else:
                    time.sleep(.000001)
                    # continue
            except OSError:
                pass


JsonDeserialize()
