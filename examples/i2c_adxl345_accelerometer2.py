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

"""
This example sets up and control an ADXL345 i2c accelerometer.
It will continuously print data the raw xyz data from the device.
"""


# the call back function to print the adxl345 data
def the_callback(data):
    """

    :param data: [pin_type, Device address, device read register, x data pair, y data pair, z data pair]
    :return:
    """
    print(data)


def adxl345(my_board):
    # setup adxl345
    # device address = 83
    my_board.set_pin_mode_i2c(i2c_port=1)

    # set up power and control register
    my_board.i2c_write(83, [45, 0], i2c_port=1)
    time.sleep(.1)
    my_board.i2c_write(83, [45, 8], i2c_port=1)
    time.sleep(.1)

    # set up the data format register
    my_board.i2c_write(83, [49, 8], i2c_port=1)
    time.sleep(.1)
    my_board.i2c_write(83, [49, 3], i2c_port=1)
    time.sleep(.1)

    # read_count = 20
    while True:
        # read 6 bytes from the data register
        try:
            my_board.i2c_read(83, 50, 6, the_callback, i2c_port=1)
            time.sleep(.1)

        except (KeyboardInterrupt, RuntimeError):
            my_board.shutdown()
            sys.exit(0)


board = telemetrix.Telemetrix()
try:
    adxl345(board)
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
