"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

"""
This example demonstrates OneWire operations by reading a  
DS18B20 or DS1822 temperature sensor.
"""

import serial
import sys
import time
from telemetrix import telemetrix


# noinspection PyArgumentList
class OneWireTemp:
    """
    This class implements reading the sensor
    """
    def __init__(self, pin):
        """

        :param pin: data pin connected to the device
        """
        self.pin = pin

        # a dictionary to determine the device type
        self.chip_types = {0x10: 'DS18S20', 0x28: 'DS18B20', 0x22: 'DS1822'}

        # callback distributor map
        # use the callback type to call the appropriate processing method
        self.callback_distribution = {31: self.search_cb, 32: self.crc_cb,
                                      25: self.reset_cb,
                                      29: self.read_cb}

        # a list to hold the detected device address
        self.address = []

        # a list to hold the measured temperature returned from device
        self.temperature_data = []

        # crc calculation result
        self.crc_comparator = None

        # instantiate the library
        try:
            self.board = telemetrix.Telemetrix()
        except (KeyboardInterrupt, serial.serialutil.SerialException):
            print('User abort')
            sys.exit(0)

        # run the program
        self.run_it()

    def run_it(self):
        """
        Access the device and print the results
        """

        # initialize OneWire operation for the pin
        self.board.set_pin_mode_one_wire(self.pin)

        # find the devices address
        self.board.onewire_search(self.onewire_callback)
        time.sleep(.3)

        if not self.address:
            print('Did not receive address')
            self.board.shutdown()
            sys.exit(0)

        # check crc of the address
        # the callback does the actual compare
        self.board.onewire_crc8(list(self.address), self.onewire_callback)
        time.sleep(.3)

        # identify and print the chip type based on the address
        chip_type = self.chip_types[self.address[0]]
        print(f'Chip detected: {chip_type}\n')
        if chip_type == 'DS18S20':
            print('This application does not support the DS18S20')
            self.board.shutdown()
            sys.exit(0)

        # reset the device, select the device and do a temperature
        # conversion
        while True:
            try:
                self.board.onewire_reset(callback=self.onewire_callback)

                # here we use skip instead of using select
                self.board.onewire_skip()

                # do a temperature conversion
                self.board.onewire_write(0x44, 1)

                # allow 1 second for the conversion to complete
                time.sleep(1)

                # reset
                self.board.onewire_reset(callback=self.onewire_callback)

                self.board.onewire_skip()

                # read the data from the scratch pad
                self.board.onewire_write(0xBE)

                for x in range(10):
                    self.board.onewire_read(self.onewire_callback)

                time.sleep(.3)

                # the temperature is contained in the first two bytes of the data
                raw = (self.temperature_data[1] << 8) | self.temperature_data[0]
                celsius = raw / 16.0
                print("Celsius = {:0.2f}º C.".format(celsius))
                fahrenheit = celsius * 1.8 + 32.0
                print("Fahrenheit = {:0.2f}º F.".format(fahrenheit))
                # clear out the buffer for the next read
                self.temperature_data = []
                print()
            except KeyboardInterrupt:
                self.board.shutdown()
                sys.exit(0)

    def onewire_callback(self, report):
        # This is the main callback distributor.
        # Call the specific handler to service the callback
        # subtype.

        # Report format: [ReportType = 14, Report Subtype, Report Data..., timestamp]

        # print(report)

        if report[1] not in self.callback_distribution:
            return  # ignore unknown types
        else:
            self.callback_distribution[report[1]](report)

    def search_cb(self, report):
        """
        Search report handler

        :param report: [ReportType = 14, Report Subtype = 31, 8 bytes of device address,
                        timestamp]
        """
        self.address = [report[x] for x in range(2, 10)]
        print('Device Address = ', " ", end="")
        for data in self.address:
            print(hex(data), " ", end="")
        print()
        self.crc_comparator = report[9]

    def crc_cb(self, report):
        """
        Crc result handler
        :param report: [ReportType = 14, Report Subtype = 21, calculated CRC byte,
                        timestamp]
        :return:
        """
        # print(f'CRC = {hex(report[2])}')
        if report[2] != self.crc_comparator:
            print('CRC Is Invalid')
            self.board.shutdown()
            sys.exit(0)

    def reset_cb(self, report):
        """
        Reset callback
        :param report: [ReportType = 14, Report Subtype = 25, reset result byte,
                        timestamp]
        """
        # not used - just ignore it
        pass

    def read_cb(self, report):
        """
        Byte read callback handler
        Append each byte received to the temperature data list
        When 9 bytes are received, check the data's CRC.

        :param report: [ReportType = 14, Report Subtype = 29, 9 temperature bytes,
                        timestamp]

        """
        self.temperature_data.append(report[2])
        if len(self.temperature_data) == 9:
            self.board.onewire_crc8(self.temperature_data, callback=self.onewire_callback)
            # hex_list = [hex(x) for x in self.temperature_data]
            # print(hex_list)
            self.crc_comparator = self.temperature_data[-1:][0]


# instantiate the class
ow = OneWireTemp(10)
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        ow.board.shutdown()
        sys.exit(0)
