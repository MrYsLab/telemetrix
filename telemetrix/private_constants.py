"""
 Copyright (c) 2015-2019 Alan Yorinks All rights reserved.

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


class PrivateConstants:
    """
    This class contains a set of constants for telemetrix internal use .
    """

    # commands
    # send a loop back request - for debugging communications
    LOOP_COMMAND = 0
    SET_PIN_MODE = 1  # set a pin to INPUT/OUTPUT/PWM/etc
    DIGITAL_WRITE = 2  # set a single digital pin value instead of entire port
    ANALOG_WRITE = 3
    MODIFY_REPORTING = 4
    GET_FIRMWARE_VERSION = 5
    ARE_U_THERE = 6  # Arduino ID query for auto-detect of telemetrix connected boards
    SERVO_ATTACH = 7
    SERVO_WRITE = 8
    SERVO_DETACH = 9
    I2C_BEGIN = 10
    I2C_READ = 11
    I2C_WRITE = 12
    SONAR_NEW = 13
    DHT_NEW = 14
    STOP_ALL_REPORTS = 15
    SET_ANALOG_SCANNING_INTERVAL = 16
    ENABLE_ALL_REPORTS = 17
    RESET = 18

    # reports
    # debug data from Arduino
    DIGITAL_REPORT = DIGITAL_WRITE
    ANALOG_REPORT = ANALOG_WRITE
    FIRMWARE_REPORT = GET_FIRMWARE_VERSION
    I_AM_HERE_REPORT = ARE_U_THERE
    SERVO_UNAVAILABLE = SERVO_ATTACH
    I2C_TOO_FEW_BYTES_RCVD = 8
    I2C_TOO_MANY_BYTES_RCVD = 9
    I2C_READ_REPORT = 10
    SONAR_DISTANCE = 11
    DHT_REPORT = 12

    DEBUG_PRINT = 99

    TELEMETRIX_VERSION = "1.7"

    # reporting control
    REPORTING_DISABLE_ALL = 0
    REPORTING_ANALOG_ENABLE = 1
    REPORTING_DIGITAL_ENABLE = 2
    REPORTING_ANALOG_DISABLE = 3
    REPORTING_DIGITAL_DISABLE = 4

    # Pin mode definitions
    AT_INPUT = 0
    AT_OUTPUT = 1
    AT_INPUT_PULLUP = 2
    AT_ANALOG = 3
    AT_SERVO = 4
    AT_SONAR = 5
    AT_DHT = 6
    AT_MODE_NOT_SET = 255

    # maximum number of digital pins supported
    NUMBER_OF_DIGITAL_PINS = 100

    # maximum number of analog pins supported
    NUMBER_OF_ANALOG_PINS = 20

    # maximum number of sonars allowed
    MAX_SONARS = 6

    # maximum number of DHT devices allowed
    MAX_DHTS = 6

    # DHT Report sub-types
    DHT_DATA = 0
    DHT_ERROR = 1
