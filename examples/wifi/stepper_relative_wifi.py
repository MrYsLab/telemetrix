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

"""

import sys
import time

from telemetrix import telemetrix

"""
Run a motor to a relative position.
"""

# Create a Telemetrix instance.
board = telemetrix.Telemetrix(ip_address='192.168.2.112')
time.sleep(.2)


def the_callback(data):
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
    print(f'Motor {data[1]} relative  motion completed at: {date}.')


# create an accelstepper instance for a TB6600 motor driver
motor = board.set_pin_mode_stepper(interface=2, pin1=5, pin2=4)

# if you are using a 28BYJ-48 Stepper Motor with ULN2003
# comment out the line above and uncomment out the line below.
# motor = board.set_pin_mode_stepper(interface=4, pin1=5, pin2=4, pin3=14, pin4=12)


# set the max speed and acceleration
board.stepper_set_max_speed(motor, 400)
board.stepper_set_acceleration(motor, 800)

# set the relative position in steps
board.stepper_move(motor, -2000)

# run the motor
board.stepper_run(motor, completion_callback=the_callback)

# keep application running
while True:
    try:
        time.sleep(.2)
    except KeyboardInterrupt:
        board.shutdown()
        sys.exit(0)
