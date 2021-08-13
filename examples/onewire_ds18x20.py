"""
 Copyright (c) 2020 Alan Yorinks All rights reserved.

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

import sys
import time
from telemetrix import telemetrix


class OneWireTemp:
    def __init__(self, pin):
        self.address = []
        self.pin = pin
        self.board = telemetrix.Telemetrix()
        self.chip_types = {0x10: 'DS18S20', 0x28: 'DS18B20', 0x22: 'DS1822'}

        self.run_it()

    def run_it(self):
        self.board.set_pin_mode_one_wire(self.pin)

        self.board.onewire_search(self.onewire_callback)
        time.sleep(.3)
        if not self.address:
            print('Did not received address')
            self.board.shutdown()
            sys.exit(0)

        # check crc
        self.board.onewire_crc8(self.address, self.onewire_callback)
        time.sleep(.3)
        # identify chip
        print(f'Chip detected: {self.chip_types[self.address[0]]}')

    def onewire_callback(self, report):
        # handle search report
        if report[1] == 31:
            self.address = [report[x] for x in range(2, 10)]
            print('Device Address = ', " ", end="")
            for data in self.address:
                print(hex(data), " ", end="")
            print()
        elif report[1] == 32:
            print(f'CRC = {hex(report[2])}')
            if report[2] != self.address[7]:
                print('CRC and Address Do Not Match')
                self.board.shutdown()
                sys.exit(0)
            else:
                print('Valid CRC')


ow = OneWireTemp(10)
while True:
    time.sleep(1)