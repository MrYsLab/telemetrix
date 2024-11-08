"""
 Copyright (c) 2015-2021 Alan Yorinks All rights reserved.

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
    SPI_INIT = 19
    SPI_WRITE_BLOCKING = 20
    SPI_READ_BLOCKING = 21
    SPI_SET_FORMAT = 22
    SPI_CS_CONTROL = 23
    ONE_WIRE_INIT = 24
    ONE_WIRE_RESET = 25
    ONE_WIRE_SELECT = 26
    ONE_WIRE_SKIP = 27
    ONE_WIRE_WRITE = 28
    ONE_WIRE_READ = 29
    ONE_WIRE_RESET_SEARCH = 30
    ONE_WIRE_SEARCH = 31
    ONE_WIRE_CRC8 = 32
    SET_PIN_MODE_STEPPER = 33
    STEPPER_MOVE_TO = 34
    STEPPER_MOVE = 35
    STEPPER_RUN = 36
    STEPPER_RUN_SPEED = 37
    STEPPER_SET_MAX_SPEED = 38
    STEPPER_SET_ACCELERATION = 39
    STEPPER_SET_SPEED = 40
    STEPPER_SET_CURRENT_POSITION = 41
    STEPPER_RUN_SPEED_TO_POSITION = 42
    STEPPER_STOP = 43
    STEPPER_DISABLE_OUTPUTS = 44
    STEPPER_ENABLE_OUTPUTS = 45
    STEPPER_SET_MINIMUM_PULSE_WIDTH = 46
    STEPPER_SET_ENABLE_PIN = 47
    STEPPER_SET_3_PINS_INVERTED = 48
    STEPPER_SET_4_PINS_INVERTED = 49
    STEPPER_IS_RUNNING = 50
    STEPPER_GET_CURRENT_POSITION = 51
    STEPPER_GET_DISTANCE_TO_GO = 52
    STEPPER_GET_TARGET_POSITION = 53
    GET_FEATURES = 54
    SONAR_DISABLE = 55
    SONAR_ENABLE = 56

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
    SPI_REPORT = 13
    ONE_WIRE_REPORT = 14
    STEPPER_DISTANCE_TO_GO = 15
    STEPPER_TARGET_POSITION = 16
    STEPPER_CURRENT_POSITION = 17
    STEPPER_RUNNING_REPORT = 18
    STEPPER_RUN_COMPLETE_REPORT = 19
    FEATURES = 20
    DEBUG_PRINT = 99

    TELEMETRIX_VERSION = "1.43"

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

    # feature masks
    ONEWIRE_FEATURE = 0x01
    DHT_FEATURE = 0x02
    STEPPERS_FEATURE = 0x04
    SPI_FEATURE = 0x08
    SERVO_FEATURE = 0x10
    SONAR_FEATURE = 0x20
