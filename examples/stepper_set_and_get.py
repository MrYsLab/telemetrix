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

"""
This file verifies the set and get methods for the stepper API.
"""
import time
from telemetrix import telemetrix


# Create a Telemetrix instance.
board = telemetrix.Telemetrix()


def current_position_callback(data):
    print(f'current_position_callback returns {data[2]}\n')


def target_position_callback(data):
    print(f'target_position_callback returns {data[2]}')


def distance_to_go_callback(data):
    print(f'distance_to_go_callback returns {data[2]}\n')


def is_running_callback(data):
    print(f'is_running_callback returns {data[1]}\n')


# create an accelstepper instance for a TB6600 motor driver
motor = board.set_pin_mode_stepper(interface=1, pin1=7, pin2=8)
print('Checking if board is running:')
board.stepper_is_running(motor, is_running_callback)
time.sleep(.2)


print('\nSetting current position to 216')
board.stepper_set_current_position(motor, 216)
board.stepper_get_current_position(motor, current_position_callback)

time.sleep(.2)

print('Setting move_to target to 300 (absolute motion.)')
board.stepper_move_to(motor, 300)
board.stepper_get_target_position(motor, target_position_callback)
time.sleep(.2)
board.stepper_get_distance_to_go(motor, distance_to_go_callback)
time.sleep(.2)

print('Setting move_to target to 300 (relative motion.)')
board.stepper_move(motor, 300)
board.stepper_get_target_position(motor, target_position_callback)
time.sleep(.2)
board.stepper_get_distance_to_go(motor, distance_to_go_callback)
time.sleep(.2)

print('Because we set all the parameters to move the motor, but have not started')
print('it yet, IS_RUNNING reports that the motor is in motion, even though it is not')
print('actually moving.')
board.stepper_is_running(motor, is_running_callback)
time.sleep(.2)
