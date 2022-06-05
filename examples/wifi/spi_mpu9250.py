# noinspection GrazieInspection
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
This example initializes an MPU9250 as an SPI device and then reads the accelerometer
and gyro values and prints them to the screen.

The processing of the data returned from the MPU9250 is done within 
the callback functions.
"""

# ESP8266 GPIO Pin      ============>     MPU9250 Pin
#
#    12 MISO                                    ADO
#    13 MOSI                                    SDA
#    14 Clock                                   SCL
#    5 Chip Select                              NCS


import sys
import time

from telemetrix import telemetrix

# Instantiate the TelemetrixRpiPico class accepting all default parameters.
board = telemetrix.Telemetrix(ip_address='192.168.2.220')


# Convenience values for the pins.
# Note that the CS value is within a list
# These are the standard pins for many Arduino AVR boards.
# Change to match your particular board.

# Chip select being used in GPIO4
CS = [5]
CS_PIN = 5

NUM_BYTES_TO_READ = 6

"""
 CALLBACKS
 
 These functions process the data returned from the MPU9250
"""


def the_device_callback(report):
    """
    Verify the device ID
    :param report: [SPI_REPORT, read register, Number of bytes, device_id]
    """
    # print(f'device_callback {report}')
    if report[3] == 0x71:
        print('MPU9250 Device ID confirmed.')
    else:
        print(f'Unexpected device ID: {report[3]}')


# noinspection GrazieInspection
def accel_callback(report):
    """
    Print the AX, AY and AZ values.
    :param report: [SPI_REPORT, Register, Number of bytes, AX-msb, AX-lsb
    AY-msb, AY-lsb, AX-msb, AX-lsb]
    """
    # print(f'accel_callback {report}')
    print(f"AX = {int.from_bytes(report[3:5], byteorder='big', signed=True)}  "
          f"AY = {int.from_bytes(report[5:7], byteorder='big', signed=True)}  "
          f"AZ = {int.from_bytes(report[7:9], byteorder='big', signed=True)}  ")


def gyro_callback(report):
    # noinspection GrazieInspection
    """
        Print the GX, GY, and GZ values.

        :param report: [SPI_REPORT, Register, Number of bytes, GX-msb, GX-lsb
        GY-msb, GY-lsb, GX-msb, GX-lsb]
        """
    # print(f'gyro_callback {report}')

    print(f"GX = {int.from_bytes(report[3:5], byteorder='big', signed=True)}  "
          f"GY = {int.from_bytes(report[5:7], byteorder='big', signed=True)}  "
          f"GZ = {int.from_bytes(report[7:9], byteorder='big', signed=True)}  ")


# This is a utility function to read SPI data
def read_data_from_device(register, number_of_bytes, callback):
    # noinspection GrazieInspection
    """
    This function reads the number of bytes using the register value.
    Data is returned via the specified callback.fg

    :param register: register value
    :param number_of_bytes: number of bytes to read
    :param callback: callback function
    """
    # the read bit is OR'ed in on the device sketch
    data = register

    # activate chip select
    board.spi_cs_control(CS_PIN, 0)

    board.spi_read_blocking(data, number_of_bytes, call_back=callback)

    # deactivate chip select
    board.spi_cs_control(CS_PIN, 1)
    time.sleep(1)


# initialize the device
board.set_pin_mode_spi(CS)

# reset the device
board.spi_cs_control(CS_PIN, 0)
board.spi_write_blocking([0x6B, 0])
board.spi_cs_control(CS_PIN, 1)

time.sleep(1)

# get the device ID
read_data_from_device(0x75, 1, the_device_callback)

while True:
    try:
        # time.sleep(1)
        # get the acceleration values
        read_data_from_device(0x3b, 6, accel_callback)
        time.sleep(1)

        # get the gyro values
        read_data_from_device(0x43, 6, gyro_callback)
        time.sleep(1)
    except KeyboardInterrupt:
        board.shutdown()
        sys.exit(0)
