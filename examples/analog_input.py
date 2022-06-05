"""
 Copyright (c) 2020 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,f
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 DHT support courtesy of Martyn Wheeler
 Based on the DHTNew library - https://github.com/RobTillaart/DHTNew
"""

import sys
import time

from telemetrix import telemetrix

"""
Monitor an analog input pin
"""

"""
Setup a pin for analog input and monitor its changes
"""

# Set up a pin for analog input and monitor its changes
ANALOG_PIN = 2  # arduino pin number (A2)

# Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3


def the_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin, current reported value, pin_mode, timestamp]
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    print(f'Pin Mode: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')


def analog_in(my_board, pin):
    """
     This function establishes the pin as an
     analog input. Any changes on this pin will
     be reported through the call back function.

     :param my_board: a telemetrix instance
     :param pin: Arduino pin number
     """

    # set the pin mode
    my_board.set_pin_mode_analog_input(pin, differential=5, callback=the_callback)

    # time.sleep(5)
    # my_board.disable_analog_reporting()
    # time.sleep(5)
    # my_board.enable_analog_reporting()

    print('Enter Control-C to quit.')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        board.shutdown()
        sys.exit(0)


board = telemetrix.Telemetrix()

try:
    analog_in(board, ANALOG_PIN)
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
