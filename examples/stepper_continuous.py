"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

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
Run a motor continuously without acceleration
"""
# GPIO Pins
PULSE_PIN = 8
DIRECTION_PIN = 9

# Create a Telemetrix instance.
board = telemetrix.Telemetrix()


# for continuous motion, the callback is not used, but provided to meet the
# API needs.
def the_callback(data):
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
    print(f'Run motor {data[1]} completed motion at: {date}.')


# create an accelstepper instance for a TB6600 motor driver
motor = board.set_pin_mode_stepper(interface=1, pin1=PULSE_PIN, pin2=DIRECTION_PIN)

try:
    while True:
        # set the max speed and speed
        board.stepper_set_max_speed(motor, 999)
        board.stepper_set_speed(motor, 500)

        # run the motor
        board.stepper_run_speed(motor)

        time.sleep(5)

        # reverse direction
        board.stepper_stop(motor)
        time.sleep(2)

        board.stepper_set_max_speed(motor, 999)
        board.stepper_set_speed(motor, -500)
        board.stepper_run_speed(motor)

        time.sleep(5)

except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)


