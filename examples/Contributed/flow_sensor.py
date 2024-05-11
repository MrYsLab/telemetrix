#    ______ _                                               
#   |  ____| |                                              
#   | |__  | | _____      __  ___  ___ _ __  ___  ___  _ __ 
#   |  __| | |/ _ \ \ /\ / / / __|/ _ \ '_ \/ __|/ _ \| '__|
#   | |    | | (_) \ V  V /  \__ \  __/ | | \__ \ (_) | |   
#   |_|    |_|\___/ \_/\_/   |___/\___|_| |_|___/\___/|_|   
#       
# https://www.dfrobot.com/product-1517.html


"""
 For support, contact  https://github.com/Pi3rr3-aprisium

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
Monitor a digital input pin with pullup enabled

Setup a pin for digital input and monitor its changes
"""

# Set up a pin for analog input and monitor its changes
DIGITAL_PIN = 2  # arduino pin number

# Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3


waterFlow = 0.0
previousValue = 0
actualValue = 0


def the_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin, current reported value, pin_mode, timestamp]
    """
    global waterFlow, previousValue, actualValue

    actualValue = data[CB_VALUE]
    # Check for transition from 0 to 1
    if previousValue == 0 and actualValue == 1:
        waterFlow += 1.0 / 650.0  # calibrated 650 units correspond to 1 liter of water

        # Print the water flow value
        print(f"Water flow: {waterFlow} L")

    # Update previousValue
    previousValue = actualValue
    return actualValue


def digital_in_pullup(my_board, pin):
    """
     This function establishes the pin as a
     digital input. Any changes on this pin will
     be reported through the call back function.

     :param my_board: a telemetrix instance
     :param pin: Arduino pin number
     """
    try:
        while True:
            my_board.set_pin_mode_digital_input_pullup(pin, the_callback)
            time.sleep(.0001)
    except KeyboardInterrupt:
        print('short loop break out')
        board.disable_digital_reporting(DIGITAL_PIN)
        board.shutdown()
        sys.exit(0)


board = telemetrix.Telemetrix()

try:
    digital_in_pullup(board, DIGITAL_PIN)
except KeyboardInterrupt:
    print('End of the readings. \nDisable de report...\nCallback clear')
    board.disable_digital_reporting(DIGITAL_PIN)
    board.shutdown()
    sys.exit(0)

