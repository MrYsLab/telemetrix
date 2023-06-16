"""
 Copyright (c) 2023 Alan Yorinks All rights reserved.

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
This program reads x, y, and z registers of an ADXL345 using 4 Wire SPI interface
"""


def the_callback(data):
    """
    :param data: [pin_type, chip select pin, device read register, x data pair,
                 y data pair, z data pair, time stamp]

    """
    report_type = data[0]
    chip_select_pin = data[1]
    device_read_register = data[2] & 0x3f  # strip off read command bits
    number_bytes_read = data[3]
    x_msb = data[4]
    x_lsb = data[5]
    y_msb = data[6]
    y_lsb = data[7]
    z_msb = data[8]
    z_lsb = data[9]

    x_data = (x_msb << 8) + x_lsb
    y_data = (y_msb << 8) + y_lsb
    z_data = (z_msb << 8) + z_lsb

    # test report type for SPI report
    if report_type == 13:
        print(f'SPI Report:  CS Pin: {chip_select_pin}   SPI Register: '
              f'{device_read_register}   Number Of Bytes Read: {number_bytes_read}    x: '
              f'{x_data}   y: {y_data}   z: {z_data}')
    else:
        print(f'unexpected report type: {report_type}')


def adxl345(my_board):
    """

    :type my_board: object
    """
    # initialize spi mode for chipselect on pin 10
    my_board.set_pin_mode_spi([10])
    time.sleep(.3)

    # set the SPI format
    # spi speed is FPU frequency divided by 4
    # data order is MSB
    # mode is MODE3
    my_board.spi_set_format(4, 1, 0x0c)
    time.sleep(.3)

    # set up power and control register
    my_board.spi_write_blocking(10, [45, 0])
    time.sleep(.3)

    my_board.spi_write_blocking(10, [45, 8])
    time.sleep(.3)

    # set up data format register for 4 wire spi
    my_board.spi_write_blocking(10, [49, 0])
    time.sleep(.3)

    # read 6 bytes from the data register
    # for a multibyte read, we need to OR in a 0x40 into the register value
    while True:
        # read 6 bytes from the data register
        try:
            my_board.spi_read_blocking(10, 50 | 0x40, 6, the_callback)

            time.sleep(.5)

        except (KeyboardInterrupt, RuntimeError):
            my_board.shutdown()
            sys.exit(0)


board = telemetrix.Telemetrix(arduino_wait=4)
try:
    adxl345(board)
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
