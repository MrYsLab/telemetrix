"""
 Copyright (c) 2022 Alan Yorinks All rights reserved.

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
Run a motor to an absolute position. Server will send a callback notification 
when motion is complete.

Motor used to test is a NEMA-17 size - 200 steps/rev, 12V 350mA.
And the driver is a TB6600 4A 9-42V Nema 17 Stepper Motor Driver.

The driver was connected as follows:
VCC 12 VDC
GND Power supply ground
ENA- Not connected
ENA+ Not connected
DIR- GND
DIR+ GPIO Pin 23 ESP32
PUL- ESP32 GND
PUL+ GPIO Pin 22 ESP32
A-, A+ Coil 1 stepper motor
B-, B+ Coil 2 stepper motor

"""

# GPIO Pins
PULSE_PIN = 8
DIRECTION_PIN = 9

# flag to keep track of the number of times the callback
# was called. When == 2, exit program
exit_flag = 0


def the_callback(data):
    global exit_flag
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
    print(f'Motor {data[1]} absolute motion completed at: {date}.')
    exit_flag += 1


def running_callback(data):
    if data[1]:
        print('The motor is running.')
    else:
        print('The motor IS NOT running.')


def step_absolute(the_board):

    global exit_flag
    # create an accelstepper instance for a TB6600 motor drive
    # if you are using a micro stepper controller board:
    # pin1 = pulse pin, pin2 = direction
    motor = the_board.set_pin_mode_stepper(interface=1, pin1=PULSE_PIN,
                                                 pin2=DIRECTION_PIN)

    # if you are using a 28BYJ-48 Stepper Motor with ULN2003
    # comment out the line above and uncomment out the line below.
    # motor = the_board.set_pin_mode_stepper(interface=4, pin1=5, pin2=4, pin3=14,
    # pin4=12)

    # the_board.stepper_is_running(motor, callback=running_callback)
    time.sleep(.5)

    # set the max speed and acceleration
    the_board.stepper_set_current_position(0, 0)
    the_board.stepper_set_max_speed(motor, 400)
    the_board.stepper_set_acceleration(motor, 800)

    # set the absolute position in steps
    the_board.stepper_move_to(motor, 2000)

    # run the motor
    print('Starting motor...')
    the_board.stepper_run(motor, completion_callback=the_callback)
    time.sleep(.2)
    the_board.stepper_is_running(motor, callback=running_callback)
    time.sleep(.2)
    while exit_flag == 0:
        time.sleep(.2)

    the_board.stepper_set_current_position(0, 0)
    the_board.stepper_set_max_speed(motor, 400)
    the_board.stepper_set_acceleration(motor, 800)
    # set the absolute position in steps
    print('Running motor in opposite direction')
    the_board.stepper_move_to(motor, -2000)

    the_board.stepper_run(motor, completion_callback=the_callback)
    time.sleep(.2)
    the_board.stepper_is_running(motor, callback=running_callback)
    time.sleep(.2)

    # keep application running
    while exit_flag < 2:
        try:
            time.sleep(.2)
        except KeyboardInterrupt:
            the_board.shutdown()
            sys.exit(0)
    the_board.shutdown()
    sys.exit(0)


# instantiate telemetrix
board = telemetrix.Telemetrix()
try:
    # start the main function
    step_absolute(board)
    board.shutdown()
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
