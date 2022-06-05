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
This program continuously monitors an HC-SR04 Ultrasonic Sensor
It reports changes to the distance sensed.
"""
TRIGGER_PIN = 4
ECHO_PIN = 5

# indices into callback data
REPORT_TYPE = 0
TRIG_PIN = 1
DISTANCE = 2
TIME = 3


# A callback function to display the distance
def the_callback(data):
    """
    The callback function to display the change in distance
    :param data: [report_type = PrivateConstants.SONAR_DISTANCE, trigger pin number, distance, timestamp]
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[3]))
    print(f'Sonar Report: Trigger Pin: {data[1]} Distance: {data[2]} Time: {date}')


def sonar(my_board, trigger_pin, echo_pin, callback):
    """
    Set the pin mode for a sonar device. Results will appear via the
    callback.

    :param my_board: a telemetrix instance
    :param trigger_pin: Arduino pin number
    :param echo_pin: Arduino pin number
    :param callback: The callback function
    """

    # set the pin mode for the trigger and echo pins
    my_board.set_pin_mode_sonar(trigger_pin, echo_pin, callback)
    # wait forever
    while True:
        try:
            time.sleep(.02)
        except KeyboardInterrupt:
            my_board.shutdown()
            sys.exit(0)


board = telemetrix.Telemetrix(ip_address='192.168.2.112')
time.sleep(.02)
try:
    sonar(board, TRIGGER_PIN, ECHO_PIN, the_callback)
    board.shutdown()
except (KeyboardInterrupt, RuntimeError):
    board.shutdown()
    sys.exit(0)
