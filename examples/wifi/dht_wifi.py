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
This program monitors a DHT 22 sensor. 
"""

# indices into callback data for valid data
# REPORT_TYPE = 0
# ERROR_CODE = 1  # value of 0 is no errors
# PIN = 2
# DHT_TYP = 3
# HUMIDITY = 4
# TEMPERATURE = 5
# TIME = 6

# indices into callback data for error report
# REPORT_TYPE = 0
# ERROR_CODE = 1 (value of 0 is no errors)
# PIN = 2
# DHT_TYPE = 3
# TIME = 4


# A callback function to display the distance
# noinspection GrazieInspection
def the_callback(data):
    """
    The callback function to display the change in distance
    :param data: [report_type = PrivateConstants.DHT, pin number, humidity, temperature timestamp]
                 if this is an error report:
                 [report_type = PrivateConstants.DHT, pin number, error value timestamp]
    """
    if data[1]:
        # error message
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[4]))
        print(f'DHT Error Report:'
              f'Pin: {data[3]} Error: {data[2]}  Time: {date}')
    else:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[6]))
        print(f'DHT Valid Data Report:'
              f'Pin: {data[3]} Humidity: {data[4]} Temperature: {data[5]} Time: {date}')


def dht(my_board):
    # noinspection GrazieInspection
    """
        Set the pin mode for a DHT 22 device. Results will appear via the
        callback.

        :param my_board: a telemetrix instance

        """

    # set the pin mode for the trigger and echo pins
    my_board.set_pin_mode_dht(5, callback=the_callback, dht_type=22)

    # wait forever
    while True:
        try:
            time.sleep(.01)
        except KeyboardInterrupt:
            my_board.shutdown()
            sys.exit(0)


board = telemetrix.Telemetrix(ip_address='192.168.2.112')
try:
    dht(board)
    board.shutdown()
except (KeyboardInterrupt, RuntimeError):
    board.shutdown()
    sys.exit(0)
