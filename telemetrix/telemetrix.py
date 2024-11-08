"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

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
import socket
import sys
import threading
import time
from collections import deque

import serial
# noinspection PyPackageRequirementscd
from serial.serialutil import SerialException
# noinspection PyPackageRequirements
from serial.tools import list_ports

# noinspection PyUnresolvedReferences
from telemetrix.private_constants import PrivateConstants

class TelemetrixPortRegister:
    """
    This is a Singleton Class to share active ports
    used by Telemetrix instances.

    """
    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = super(TelemetrixPortRegister, self).__new__(self)
            self.active = []
        return self._instance

    def add(self, port):
        self.active.append(port)

# noinspection PyPep8,PyMethodMayBeStatic,GrazieInspection,PyBroadException,PyCallingNonCallable
class Telemetrix(threading.Thread):
    """
    This class exposes and implements the telemetrix API.
    It uses threading to accommodate concurrency.
    It includes the public API methods as well as
    a set of private methods.

    """

    # noinspection PyPep8,PyPep8,PyPep8
    def __init__(self, com_port=None, arduino_instance_id=1,
                 arduino_wait=4, sleep_tune=0.000001,
                 shutdown_on_exception=True,
                 ip_address=None, ip_port=31335):

        self.serial_port_register = TelemetrixPortRegister()
        """

        :param com_port: e.g. COM3 or /dev/ttyACM0.
                         Only use if you wish to bypass auto com port
                         detection.

        :param arduino_instance_id: Match with the value installed on the
                                    arduino-telemetrix sketch.

        :param arduino_wait: Amount of time to wait for an Arduino to
                             fully reset itself.

        :param sleep_tune: A tuning parameter (typically not changed by user)

        :param shutdown_on_exception: call shutdown before raising
                                      a RunTimeError exception, or
                                      receiving a KeyboardInterrupt exception

        :param ip_address: ip address of tcp/ip connected device.

        :param ip_port: ip port of tcp/ip connected device
        """

        # initialize threading parent
        threading.Thread.__init__(self)

        # create the threads and set them as daemons so
        # that they stop when the program is closed

        # create a thread to interpret received serial data
        self.the_reporter_thread = threading.Thread(target=self._reporter)
        self.the_reporter_thread.daemon = True

        self.ip_address = ip_address
        self.ip_port = ip_port

        if not self.ip_address:
            self.the_data_receive_thread = threading.Thread(target=self._serial_receiver)
        else:
            self.the_data_receive_thread = threading.Thread(target=self._tcp_receiver)

        self.the_data_receive_thread.daemon = True

        # flag to allow the reporter and receive threads to run.
        self.run_event = threading.Event()

        # check to make sure that Python interpreter is version 3.7 or greater
        python_version = sys.version_info
        if python_version[0] >= 3:
            if python_version[1] >= 7:
                pass
            else:
                raise RuntimeError("ERROR: Python 3.7 or greater is "
                                   "required for use of this program.")

        # save input parameters as instance variables
        self.com_port = com_port
        self.arduino_instance_id = arduino_instance_id
        self.arduino_wait = arduino_wait
        self.sleep_tune = sleep_tune
        self.shutdown_on_exception = shutdown_on_exception

        # create a deque to receive and process data from the arduino
        self.the_deque = deque()

        # The report_dispatch dictionary is used to process
        # incoming report messages by looking up the report message
        # and executing its associated processing method.

        self.report_dispatch = {}

        # To add a command to the command dispatch table, append here.
        self.report_dispatch.update(
            {PrivateConstants.LOOP_COMMAND: self._report_loop_data})
        self.report_dispatch.update(
            {PrivateConstants.DEBUG_PRINT: self._report_debug_data})
        self.report_dispatch.update(
            {PrivateConstants.DIGITAL_REPORT: self._digital_message})
        self.report_dispatch.update(
            {PrivateConstants.ANALOG_REPORT: self._analog_message})
        self.report_dispatch.update(
            {PrivateConstants.FIRMWARE_REPORT: self._firmware_message})
        self.report_dispatch.update({PrivateConstants.I_AM_HERE_REPORT: self._i_am_here})
        self.report_dispatch.update(
            {PrivateConstants.SERVO_UNAVAILABLE: self._servo_unavailable})
        self.report_dispatch.update(
            {PrivateConstants.I2C_READ_REPORT: self._i2c_read_report})
        self.report_dispatch.update(
            {PrivateConstants.I2C_TOO_FEW_BYTES_RCVD: self._i2c_too_few})
        self.report_dispatch.update(
            {PrivateConstants.I2C_TOO_MANY_BYTES_RCVD: self._i2c_too_many})
        self.report_dispatch.update(
            {PrivateConstants.SONAR_DISTANCE: self._sonar_distance_report})
        self.report_dispatch.update({PrivateConstants.DHT_REPORT: self._dht_report})
        self.report_dispatch.update(
            {PrivateConstants.SPI_REPORT: self._spi_report})
        self.report_dispatch.update(
            {PrivateConstants.ONE_WIRE_REPORT: self._onewire_report})
        self.report_dispatch.update(
            {PrivateConstants.STEPPER_DISTANCE_TO_GO:
                 self._stepper_distance_to_go_report})
        self.report_dispatch.update(
            {PrivateConstants.STEPPER_TARGET_POSITION:
                 self._stepper_target_position_report})
        self.report_dispatch.update(
            {PrivateConstants.STEPPER_CURRENT_POSITION:
                 self._stepper_current_position_report})
        self.report_dispatch.update(
            {PrivateConstants.STEPPER_RUNNING_REPORT:
                 self._stepper_is_running_report})
        self.report_dispatch.update(
            {PrivateConstants.STEPPER_RUN_COMPLETE_REPORT:
                 self._stepper_run_complete_report})

        self.report_dispatch.update(
            {PrivateConstants.STEPPER_DISTANCE_TO_GO:
                 self._stepper_distance_to_go_report})
        self.report_dispatch.update(
            {PrivateConstants.STEPPER_TARGET_POSITION:
                 self._stepper_target_position_report})
        self.report_dispatch.update(
            {PrivateConstants.FEATURES:
                 self._features_report})

        # dictionaries to store the callbacks for each pin
        self.analog_callbacks = {}

        self.digital_callbacks = {}

        self.i2c_callback = None
        self.i2c_callback2 = None

        self.i2c_1_active = False
        self.i2c_2_active = False

        self.spi_callback = None

        self.onewire_callback = None

        self.cs_pins_enabled = []

        # the trigger pin will be the key to retrieve
        # the callback for a specific HC-SR04
        self.sonar_callbacks = {}

        self.sonar_count = 0

        self.dht_callbacks = {}

        self.dht_count = 0

        # serial port in use
        self.serial_port = None

        # socket for tcp/ip communications
        self.sock = None

        # flag to indicate we are in shutdown mode
        self.shutdown_flag = False

        # debug loopback callback method
        self.loop_back_callback = None

        # flag to indicate the start of a new report
        # self.new_report_start = True

        # firmware version to be stored here
        self.firmware_version = []

        # reported arduino instance id
        self.reported_arduino_id = None

        # reported features
        self.reported_features = 0

        # flag to indicate if i2c was previously enabled
        self.i2c_enabled = False

        # flag to indicate if spi is initialized
        self.spi_enabled = False

        # flag to indicate if onewire is initialized
        self.onewire_enabled = False

        # stepper motor variables

        # updated when a new motor is added
        self.next_stepper_assigned = 0

        # valid list of stepper motor interface types
        self.valid_stepper_interfaces = [1, 2, 3, 4, 6, 8]

        # maximum number of steppers supported
        self.max_number_of_steppers = 8

        # number of steppers created - not to exceed the maximum
        self.number_of_steppers = 0

        # dictionary to hold stepper motor information
        self.stepper_info = {'instance': False, 'is_running': None,
                             'maximum_speed': 1, 'speed': 0, 'acceleration': 0,
                             'distance_to_go_callback': None,
                             'target_position_callback': None,
                             'current_position_callback': None,
                             'is_running_callback': None,
                             'motion_complete_callback': None,
                             'acceleration_callback': None}

        # build a list of stepper motor info items
        self.stepper_info_list = []
        # a list of dictionaries to hold stepper information
        for motor in range(self.max_number_of_steppers):
            self.stepper_info_list.append(self.stepper_info.copy())

        self.the_reporter_thread.start()
        self.the_data_receive_thread.start()

        print(f"Telemetrix:  Version {PrivateConstants.TELEMETRIX_VERSION}\n\n"
              f"Copyright (c) 2021 Alan Yorinks All Rights Reserved.\n")

        # using the serial link
        if not self.ip_address:
            if not self.com_port:
                # user did not specify a com_port
                try:
                    self._find_arduino()
                except KeyboardInterrupt:
                    if self.shutdown_on_exception:
                        self.shutdown()
            else:
                # com_port specified - set com_port and baud rate
                try:
                    self._manual_open()
                except KeyboardInterrupt:
                    if self.shutdown_on_exception:
                        self.shutdown()

            if self.serial_port:
                print(
                    f"Arduino compatible device found and connected to {self.serial_port.port}")

                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()

            # no com_port found - raise a runtime exception
            else:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('No Arduino Found or User Aborted Program')
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip_address, self.ip_port))
            print(f'Successfully connected to: {self.ip_address}:{self.ip_port}')

        # allow the threads to run
        self._run_threads()
        print(f'Waiting for Arduino to reset')
        print(f'Reset Complete')

        # get telemetrix firmware version and print it
        print('\nRetrieving Telemetrix4Arduino firmware ID...')
        self._get_firmware_version()
        if not self.firmware_version:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'Telemetrix4Arduino firmware version')

        else:
            # if self.firmware_version[0] < 5:
            #   raise RuntimeError('Please upgrade the server firmware to version '
            #                        '5.0.0 or greater')
            print(f'Telemetrix4Arduino firmware version: {self.firmware_version[0]}.'
                  f'{self.firmware_version[1]}.{self.firmware_version[2]}')
        command = [PrivateConstants.ENABLE_ALL_REPORTS]
        self._send_command(command)

        # get the features list
        command = [PrivateConstants.GET_FEATURES]
        self._send_command(command)
        time.sleep(.2)

        # Have the server reset its data structures
        command = [PrivateConstants.RESET]
        self._send_command(command)

    def _find_arduino(self):
        """
        This method will search all potential serial ports for an Arduino
        containing a sketch that has a matching arduino_instance_id as
        specified in the input parameters of this class.

        This is used explicitly with the Telemetrix4Arduino sketch.
        """

        # a list of serial ports to be checked
        serial_ports = []

        print('Opening all potential serial ports...')
        the_ports_list = list_ports.comports()

        registered_ports = list(map(lambda p: p.port, self.serial_port_register.active))
        for port in the_ports_list:
            if port.pid is None or port.device in registered_ports:
                continue
            try:
                self.serial_port = serial.Serial(port.device, 115200,
                                                 timeout=1, writeTimeout=0)
            except SerialException:
                continue
            # create a list of serial ports that we opened
            serial_ports.append(self.serial_port)

            # display to the user
            print('\t' + port.device)

            # clear out any possible data in the input buffer
        # wait for arduino to reset
        print(
            f'\nWaiting {self.arduino_wait} seconds(arduino_wait) for Arduino devices to '
            'reset...')
        # temporary for testing
        time.sleep(self.arduino_wait)
        self._run_threads()

        for serial_port in serial_ports:
            self.serial_port = serial_port

            # Since opening the port, there might be e.g., boot logs in the
            # buffer. Clear them before proceeding.
            self.serial_port.reset_input_buffer()

            self._get_arduino_id()
            retries = 50
            while self.reported_arduino_id is None and retries > 0:
                time.sleep(.2)
                retries -= 1
            if self.reported_arduino_id != self.arduino_instance_id:
                continue
            else:
                self.serial_port_register.add(serial_port)
                print('Valid Arduino ID Found.')
                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()
                return
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(f'Incorrect Arduino ID: {self.reported_arduino_id}')

    def _manual_open(self):
        """
        Com port was specified by the user - try to open up that port

        """
        # if port is not found, a serial exception will be thrown
        try:
            print(f'Opening {self.com_port}...')
            self.serial_port = serial.Serial(self.com_port, 115200,
                                             timeout=1, writeTimeout=0)

            print(
                f'\nWaiting {self.arduino_wait} seconds(arduino_wait) for Arduino devices to '
                'reset...')
            self._run_threads()
            time.sleep(self.arduino_wait)

            self._get_arduino_id()

            if self.reported_arduino_id != self.arduino_instance_id:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(f'Incorrect Arduino ID: {self.reported_arduino_id}')
            print('Valid Arduino ID Found.')
            # get arduino firmware version and print it
            print('\nRetrieving Telemetrix4Arduino firmware ID...')
            self._get_firmware_version()

            if not self.firmware_version:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    f'Telemetrix4Arduino Sketch Firmware Version Not Found')

            else:
                print(f'Telemetrix4Arduino firmware version: {self.firmware_version[0]}.'
                      f'{self.firmware_version[1]}')
        except KeyboardInterrupt:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('User Hit Control-C')

    def analog_write(self, pin, value):
        """
        Set the specified pin to the specified value.

        :param pin: arduino pin number

        :param value: pin value (maximum 16 bits)

        """
        value_msb = value >> 8
        value_lsb = value & 0xff
        command = [PrivateConstants.ANALOG_WRITE, pin, value_msb, value_lsb]
        self._send_command(command)

    def digital_write(self, pin, value):
        """
        Set the specified pin to the specified value.

        :param pin: arduino pin number

        :param value: pin value (1 or 0)

        """

        command = [PrivateConstants.DIGITAL_WRITE, pin, value]
        self._send_command(command)

    def disable_all_reporting(self):
        """
        Disable reporting for all digital and analog input pins
        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_DISABLE_ALL, 0]
        self._send_command(command)

    def disable_analog_reporting(self, pin):
        """
        Disables analog reporting for a single analog pin.

        :param pin: Analog pin number. For example for A0, the number is 0.

        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_ANALOG_DISABLE, pin]
        self._send_command(command)

    def disable_digital_reporting(self, pin):
        """
        Disables digital reporting for a single digital input.

        :param pin: Pin number.

        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_DIGITAL_DISABLE, pin]
        self._send_command(command)

    def enable_analog_reporting(self, pin):
        """
        Enables analog reporting for the specified pin.

        :param pin: Analog pin number. For example for A0, the number is 0.


        """
        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_ANALOG_ENABLE, pin]
        self._send_command(command)

    def enable_digital_reporting(self, pin):
        """
        Enable reporting on the specified digital pin.

        :param pin: Pin number.
        """

        command = [PrivateConstants.MODIFY_REPORTING,
                   PrivateConstants.REPORTING_DIGITAL_ENABLE, pin]
        self._send_command(command)

    def _get_arduino_id(self):
        """
        Retrieve arduino-telemetrix arduino id

        """
        command = [PrivateConstants.ARE_U_THERE]
        self._send_command(command)
        # provide time for the reply
        time.sleep(.5)

    def _get_firmware_version(self):
        """
        This method retrieves the
        arduino-telemetrix firmware version

        """
        command = [PrivateConstants.GET_FIRMWARE_VERSION]
        self._send_command(command)
        # provide time for the reply
        time.sleep(.5)

    def i2c_read(self, address, register, number_of_bytes,
                 callback=None, i2c_port=0,
                 write_register=True):
        """
        Read the specified number of bytes from the
        specified register for the i2c device.


        :param address: i2c device address

        :param register: i2c register (or None if no register
                                       selection is needed)

        :param number_of_bytes: number of bytes to be read

        :param callback: Required callback function to report
                         i2c data as a result of read command

       :param i2c_port: 0 = default, 1 = secondary

       :param write_register: If True, the register is written
                                       before read
                              Else, the write is suppressed


        callback returns a data list:

        [I2C_READ_REPORT, i2c_port, number of bytes read, address, register,
        bytes read..., time-stamp]


        """

        self._i2c_read_request(address, register, number_of_bytes,
                               callback=callback, i2c_port=i2c_port,
                               write_register=write_register)

    def i2c_read_restart_transmission(self, address, register,
                                      number_of_bytes,
                                      callback=None, i2c_port=0,
                                      write_register=True):
        """
        Read the specified number of bytes from the specified
        register for the i2c device. This restarts the transmission
        after the read. It is required for some i2c devices such as the MMA8452Q
        accelerometer.


        :param address: i2c device address

        :param register: i2c register (or None if no register
                                                    selection is needed)

        :param number_of_bytes: number of bytes to be read

        :param callback: Required callback function to report i2c
                         data as a result of read command

       :param i2c_port: 0 = default 1 = secondary

       :param write_register: If True, the register is written before read
                              Else, the write is suppressed



        callback returns a data list:

        [I2C_READ_REPORT, i2c_port, number of bytes read, address, register,
        bytes read..., time-stamp]

        """

        self._i2c_read_request(address, register, number_of_bytes,
                               stop_transmission=False,
                               callback=callback, i2c_port=i2c_port,
                               write_register=write_register)

    def _i2c_read_request(self, address, register, number_of_bytes,
                          stop_transmission=True, callback=None, i2c_port=0,
                          write_register=True):
        """
        This method requests the read of an i2c device. Results are retrieved
        via callback.

        :param address: i2c device address

        :param register: register number (or None if no register selection is needed)

        :param number_of_bytes: number of bytes expected to be returned

        :param stop_transmission: stop transmission after read

        :param callback: Required callback function to report i2c data as a
                   result of read command.

       :param write_register: If True, the register is written before read
                              Else, the write is suppressed

        """
        if not i2c_port:
            if not self.i2c_1_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Read: set_pin_mode i2c never called for i2c port 1.')

        if i2c_port:
            if not self.i2c_2_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Read: set_pin_mode i2c never called for i2c port 2.')

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('I2C Read: A callback function must be specified.')

        if not i2c_port:
            self.i2c_callback = callback
        else:
            self.i2c_callback2 = callback

        if not register:
            register = 0

        if write_register:
            write_register = 1
        else:
            write_register = 0

        # message contains:
        # 1. address
        # 2. register
        # 3. number of bytes
        # 4. restart_transmission - True or False
        # 5. i2c port
        # 6. suppress write flag

        command = [PrivateConstants.I2C_READ, address, register, number_of_bytes,
                   stop_transmission, i2c_port, write_register]
        self._send_command(command)

    def i2c_write(self, address, args, i2c_port=0):
        """
        Write data to an i2c device.

        :param address: i2c device address

        :param i2c_port: 0= port 1, 1 = port 2

        :param args: A variable number of bytes to be sent to the device
                     passed in as a list

        """
        if not i2c_port:
            if not self.i2c_1_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Write: set_pin_mode i2c never called for i2c port 1.')

        if i2c_port:
            if not self.i2c_2_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    'I2C Write: set_pin_mode i2c never called for i2c port 2.')

        command = [PrivateConstants.I2C_WRITE, len(args), address, i2c_port]

        for item in args:
            command.append(item)

        self._send_command(command)

    def loop_back(self, start_character, callback=None):
        """
        This is a debugging method to send a character to the
        Arduino device, and have the device loop it back.

        :param start_character: The character to loop back. It should be
                                an integer.

        :param callback: Looped back character will appear in the callback method

        """
        command = [PrivateConstants.LOOP_COMMAND, ord(start_character)]
        self.loop_back_callback = callback
        self._send_command(command)

    def set_analog_scan_interval(self, interval):
        """
        Set the analog scanning interval.

        :param interval: value of 0 - 255 - milliseconds
        """

        if 0 <= interval <= 255:
            command = [PrivateConstants.SET_ANALOG_SCANNING_INTERVAL, interval]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('Analog interval must be between 0 and 255')

    def set_pin_mode_analog_output(self, pin_number):
        """
        Set a pin as a pwm (analog output) pin.

        :param pin_number:arduino pin number

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_OUTPUT)

    def set_pin_mode_analog_input(self, pin_number, differential=0, callback=None):
        """
        Set a pin as an analog input.

        :param pin_number: arduino pin number

        :param differential: difference in previous to current value before
                             report will be generated

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for analog input pins = 3

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_ANALOG, differential,
                           callback)

    def set_pin_mode_digital_input(self, pin_number, callback=None):
        """
        Set a pin as a digital input.

        :param pin_number: arduino pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for all digital input pins = 2

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT, callback=callback)

    def set_pin_mode_digital_input_pullup(self, pin_number, callback=None):
        """
        Set a pin as a digital input with pullup enabled.

        :param pin_number: arduino pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for all digital input pins = 2
        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT_PULLUP,
                           callback=callback)

    def set_pin_mode_digital_output(self, pin_number):
        """
        Set a pin as a digital output pin.

        :param pin_number: arduino pin number
        """

        self._set_pin_mode(pin_number, PrivateConstants.AT_OUTPUT)

    def set_pin_mode_i2c(self, i2c_port=0):
        """
        Establish the standard Arduino i2c pins for i2c utilization.

        :param i2c_port: 0 = i2c1, 1 = i2c2

        NOTES: 1. THIS METHOD MUST BE CALLED BEFORE ANY I2C REQUEST IS MADE
               2. Callbacks are set within the individual i2c read methods of this
              API.

              See i2c_read, or i2c_read_restart_transmission.

        """
        # test for i2c port 2
        if i2c_port:
            # if not previously activated set it to activated
            # and the send a begin message for this port
            if not self.i2c_2_active:
                self.i2c_2_active = True
            else:
                return
        # port 1
        else:
            if not self.i2c_1_active:
                self.i2c_1_active = True
            else:
                return

        command = [PrivateConstants.I2C_BEGIN, i2c_port]
        self._send_command(command)

    def set_pin_mode_dht(self, pin, callback=None, dht_type=22):
        """

        :param pin: connection pin

        :param callback: callback function

        :param dht_type: either 22 for DHT22 or 11 for DHT11

        Error Callback: [DHT REPORT Type, DHT_ERROR_NUMBER, PIN, DHT_TYPE, Time]

        Valid Data Callback: DHT REPORT Type, DHT_DATA=, PIN, DHT_TYPE, Humidity,
        Temperature,
        Time]

        DHT_REPORT_TYPE = 12
        """
        if self.reported_features & PrivateConstants.DHT_FEATURE:
            if not callback:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('set_pin_mode_dht: A Callback must be specified')

            if self.dht_count < PrivateConstants.MAX_DHTS - 1:
                if pin in self.dht_callbacks.keys():
                    if self.shutdown_on_exception:
                        self.shutdown()
                    raise RuntimeError(f'set_pin_mode_dht Pin {pin} already assigned')
                self.dht_callbacks[pin] = callback
                self.dht_count += 1

                if dht_type != 22 and dht_type != 11:
                    dht_type = 22

                command = [PrivateConstants.DHT_NEW, pin, dht_type]
                self._send_command(command)
            else:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    f'Maximum Number Of DHTs Exceeded - set_pin_mode_dht fails for pin {pin}')
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'The DHT feature is disabled in the server.')

    # noinspection PyRedundantParentheses
    def set_pin_mode_servo(self, pin_number, min_pulse=544, max_pulse=2400):
        """

        Attach a pin to a servo motor

        :param pin_number: pin

        :param min_pulse: minimum pulse width

        :param max_pulse: maximum pulse width

        """
        if self.reported_features & PrivateConstants.SERVO_FEATURE:

            minv = (min_pulse).to_bytes(2, byteorder="big")
            maxv = (max_pulse).to_bytes(2, byteorder="big")

            command = [PrivateConstants.SERVO_ATTACH, pin_number,
                       minv[0], minv[1], maxv[0], maxv[1]]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'The SERVO feature is disabled in the server.')

    def set_pin_mode_sonar(self, trigger_pin, echo_pin,
                           callback=None):
        """

        :param trigger_pin:

        :param echo_pin:

        :param callback: callback

        callback data: [PrivateConstants.SONAR_DISTANCE, trigger_pin, distance_value, time_stamp]

        """
        if self.reported_features & PrivateConstants.SONAR_FEATURE:

            if not callback:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('set_pin_mode_sonar: A Callback must be specified')

            if self.sonar_count < PrivateConstants.MAX_SONARS - 1:
                self.sonar_callbacks[trigger_pin] = callback
                self.sonar_count += 1

                command = [PrivateConstants.SONAR_NEW, trigger_pin, echo_pin]
                self._send_command(command)
            else:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError(
                    f'Maximum Number Of Sonars Exceeded - set_pin_mode_sonar fails for pin {trigger_pin}')
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'The SONAR feature is disabled in the server.')

    def set_pin_mode_spi(self, chip_select_list=None):
        """
        Specify the list of chip select pins.

        Standard Arduino MISO, MOSI and CLK pins are used for the board in use.

        Chip Select is any digital output capable pin.

        :param chip_select_list: this is a list of pins to be used for chip select.
                           The pins will be configured as output, and set to high
                           ready to be used for chip select.
                           NOTE: You must specify the chips select pins here!


        command message: [command, number of cs pins, [cs pins...]]
        """

        if self.reported_features & PrivateConstants.SPI_FEATURE:
            if type(chip_select_list) is not list:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('chip_select_list must be in the form of a list')
            if not chip_select_list:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('Chip select pins were not specified')

            self.spi_enabled = True

            command = [PrivateConstants.SPI_INIT, len(chip_select_list)]

            for pin in chip_select_list:
                command.append(pin)
                self.cs_pins_enabled.append(pin)
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'The SPI feature is disabled in the server.')

    def set_pin_mode_stepper(self, interface=1, pin1=2, pin2=3, pin3=4,
                             pin4=5, enable=True):
        """
        Stepper motor support is implemented as a proxy for the
        the AccelStepper library for the Arduino.

        https://github.com/waspinator/AccelStepper

        Instantiate a stepper motor.

        Initialize the interface and pins for a stepper motor.

        :param interface: Motor Interface Type:

                1 = Stepper Driver, 2 driver pins required

                2 = FULL2WIRE  2 wire stepper, 2 motor pins required

                3 = FULL3WIRE 3 wire stepper, such as HDD spindle,
                    3 motor pins required

                4 = FULL4WIRE, 4 wire full stepper, 4 motor pins
                    required

                6 = HALF3WIRE, 3 wire half stepper, such as HDD spindle,
                    3 motor pins required

                8 = HALF4WIRE, 4 wire half stepper, 4 motor pins required

        :param pin1: Arduino digital pin number for motor pin 1

        :param pin2: Arduino digital pin number for motor pin 2

        :param pin3: Arduino digital pin number for motor pin 3

        :param pin4: Arduino digital pin number for motor pin 4

        :param enable: If this is true, the output pins at construction time.

        :return: Motor Reference number
        """
        if self.reported_features & PrivateConstants.STEPPERS_FEATURE:

            if self.number_of_steppers == self.max_number_of_steppers:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('Maximum number of steppers has already been assigned')

            if interface not in self.valid_stepper_interfaces:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('Invalid stepper interface')

            self.number_of_steppers += 1

            motor_id = self.next_stepper_assigned
            self.next_stepper_assigned += 1
            self.stepper_info_list[motor_id]['instance'] = True

            # build message and send message to server
            command = [PrivateConstants.SET_PIN_MODE_STEPPER, motor_id, interface, pin1,
                       pin2, pin3, pin4, enable]
            self._send_command(command)

            # return motor id
            return motor_id
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'The Stepper feature is disabled in the server.')

    def servo_write(self, pin_number, angle):
        """

        Set a servo attached to a pin to a given angle.

        :param pin_number: pin

        :param angle: angle (0-180)

        """
        command = [PrivateConstants.SERVO_WRITE, pin_number, angle]
        self._send_command(command)

    def servo_detach(self, pin_number):
        """
        Detach a servo for reuse

        :param pin_number: attached pin

        """
        command = [PrivateConstants.SERVO_DETACH, pin_number]
        self._send_command(command)

    def stepper_move_to(self, motor_id, position):
        """
        Set an absolution target position. If position is positive, the movement is
        clockwise, else it is counter-clockwise.

        The run() function (below) will try to move the motor (at most one step per call)
        from the current position to the target position set by the most
        recent call to this function. Caution: moveTo() also recalculates the
        speed for the next step.
        If you are trying to use constant speed movements, you should call setSpeed()
        after calling moveTo().

        :param motor_id: motor id: 0 - 7

        :param position: target position. Maximum value is 32 bits.
        """
        if position < 0:
            polarity = 1
        else:
            polarity = 0
        position = abs(position)
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_move_to: Invalid motor_id.')

        position_bytes = list(position.to_bytes(4, 'big', signed=True))

        command = [PrivateConstants.STEPPER_MOVE_TO, motor_id]
        for value in position_bytes:
            command.append(value)
        command.append(polarity)
        self._send_command(command)

    def stepper_move(self, motor_id, relative_position):
        """
        Set the target position relative to the current position.

        :param motor_id: motor id: 0 - 7

        :param relative_position: The desired position relative to the current
                                  position. Negative is anticlockwise from
                                  the current position. Maximum value is 32 bits.
        """
        if relative_position < 0:
            polarity = 1
        else:
            polarity = 0

        relative_position = abs(relative_position)
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_move: Invalid motor_id.')

        position_bytes = list(relative_position.to_bytes(4, 'big', signed=True))

        command = [PrivateConstants.STEPPER_MOVE, motor_id]
        for value in position_bytes:
            command.append(value)
        command.append(polarity)
        self._send_command(command)

    def stepper_run(self, motor_id, completion_callback=None):
        """
        This method steps the selected motor based on the current speed.

        Once called, the server will continuously attempt to step the motor.

        :param motor_id: 0 - 7

        :param completion_callback: call back function to receive motion complete
                                    notification

        callback returns a data list:

        [report_type, motor_id, raw_time_stamp]

        The report_type = 19
        """
        if not completion_callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_run: A motion complete callback must be '
                               'specified.')

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_run: Invalid motor_id.')

        self.stepper_info_list[motor_id]['motion_complete_callback'] = completion_callback
        command = [PrivateConstants.STEPPER_RUN, motor_id]
        self._send_command(command)

    def stepper_run_speed(self, motor_id):
        """
        This method steps the selected motor based at a constant speed as set by the most
        recent call to stepper_set_max_speed(). The motor will run continuously.

        Once called, the server will continuously attempt to step the motor.

        :param motor_id: 0 - 7

        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_run_speed: Invalid motor_id.')

        command = [PrivateConstants.STEPPER_RUN_SPEED, motor_id]
        self._send_command(command)

    def stepper_set_max_speed(self, motor_id, max_speed):
        """
        Sets the maximum permitted speed. The stepper_run() function will accelerate
        up to the speed set by this function.

        Caution: the maximum speed achievable depends on your processor and clock speed.
        The default maxSpeed is 1 step per second.

         Caution: Speeds that exceed the maximum speed supported by the processor may
                  result in non-linear accelerations and decelerations.

        :param motor_id: 0 - 7

        :param max_speed: 1 - 1000
        """

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_max_speed: Invalid motor_id.')

        if not 1 < max_speed <= 1000:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_max_speed: Speed range is 1 - 1000.')

        self.stepper_info_list[motor_id]['max_speed'] = max_speed
        max_speed_msb = (max_speed & 0xff00) >> 8
        max_speed_lsb = max_speed & 0xff

        command = [PrivateConstants.STEPPER_SET_MAX_SPEED, motor_id, max_speed_msb,
                   max_speed_lsb]
        self._send_command(command)

    def stepper_get_max_speed(self, motor_id):
        """
        Returns the maximum speed configured for this stepper
        that was previously set by stepper_set_max_speed()

        Value is stored in the client, so no callback is required.

        :param motor_id: 0 - 7

        :return: The currently configured maximum speed.
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_max_speed: Invalid motor_id.')

        return self.stepper_info_list[motor_id]['max_speed']

    def stepper_set_acceleration(self, motor_id, acceleration):
        """
        Sets the acceleration/deceleration rate.

        :param motor_id: 0 - 7

        :param acceleration: The desired acceleration in steps per second
                             per second. Must be > 0.0. This is an
                             expensive call since it requires a square
                             root to be calculated on the server.
                             Dont call more often than needed.

        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_acceleration: Invalid motor_id.')

        if not 1 < acceleration <= 1000:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_acceleration: Acceleration range is 1 - '
                               '1000.')

        self.stepper_info_list[motor_id]['acceleration'] = acceleration

        max_accel_msb = acceleration >> 8
        max_accel_lsb = acceleration & 0xff

        command = [PrivateConstants.STEPPER_SET_ACCELERATION, motor_id, max_accel_msb,
                   max_accel_lsb]
        self._send_command(command)

    def stepper_set_speed(self, motor_id, speed):
        """
        Sets the desired constant speed for use with stepper_run_speed().

        :param motor_id: 0 - 7

        :param speed: -1000 - 1000 The desired constant speed in steps per
                      second. Positive is clockwise. Speeds of more than 1000 steps per
                      second are unreliable. Speed accuracy depends on the Arduino
                      crystal. Jitter depends on how frequently you call the
                      stepper_run_speed() method.
                      The speed will be limited by the current value of
                      stepper_set_max_speed().
        """

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_speed: Invalid motor_id.')

        if not -1000 <= speed <= 1000:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_speed: speed range is -1000 to 1000')

        if speed < 0:
            polarity = 1
        else:
            polarity = 0

        speed = abs(speed)
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_move: Invalid motor_id.')

        position_bytes = list(speed.to_bytes(2, 'big', signed=True))

        command = [PrivateConstants.STEPPER_SET_SPEED, motor_id]
        for value in position_bytes:
            command.append(value)
        command.append(polarity)
        self._send_command(command)

    def stepper_get_speed(self, motor_id):
        """
        Returns the  most recently set speed.
        that was previously set by stepper_set_speed();

        Value is stored in the client, so no callback is required.

        :param motor_id:  0 - 7

        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_get_speed: Invalid motor_id.')

        return self.stepper_info_list[motor_id]['speed']

    def stepper_get_distance_to_go(self, motor_id, distance_to_go_callback):
        """
        Request the distance from the current position to the target position
        from the server.

        :param motor_id: 0 - 7

        :param distance_to_go_callback: required callback function to receive report

        :return: The distance to go is returned via the callback as a list:

        [REPORT_TYPE=15, motor_id, distance in steps, time_stamp]

        A positive distance is clockwise from the current position.

        """
        if not distance_to_go_callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_get_distance_to_go Read: A callback function must be specified.')

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_get_distance_to_go: Invalid motor_id.')
        self.stepper_info_list[motor_id][
            'distance_to_go_callback'] = distance_to_go_callback
        command = [PrivateConstants.STEPPER_GET_DISTANCE_TO_GO, motor_id]
        self._send_command(command)

    def stepper_get_target_position(self, motor_id, target_callback):
        """
        Request the most recently set target position from the server.

        :param motor_id: 0 - 7

        :param target_callback: required callback function to receive report

        :return: The distance to go is returned via the callback as a list:

        [REPORT_TYPE=16, motor_id, target position in steps, time_stamp]

        Positive is clockwise from the 0 position.

        """
        if not target_callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(
                'stepper_get_target_position Read: A callback function must be specified.')

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_get_target_position: Invalid motor_id.')

        self.stepper_info_list[motor_id][
            'target_position_callback'] = target_callback

        command = [PrivateConstants.STEPPER_GET_TARGET_POSITION, motor_id]
        self._send_command(command)

    def stepper_get_current_position(self, motor_id, current_position_callback):
        """
        Request the current motor position from the server.

        :param motor_id: 0 - 7

        :param current_position_callback: required callback function to receive report

        :return: The current motor position returned via the callback as a list:

        [REPORT_TYPE=17, motor_id, current position in steps, time_stamp]

        Positive is clockwise from the 0 position.
        """
        if not current_position_callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(
                'stepper_get_current_position Read: A callback function must be specified.')

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_get_current_position: Invalid motor_id.')

        self.stepper_info_list[motor_id]['current_position_callback'] = current_position_callback

        command = [PrivateConstants.STEPPER_GET_CURRENT_POSITION, motor_id]
        self._send_command(command)

    def stepper_set_current_position(self, motor_id, position):
        """
        Resets the current position of the motor, so that wherever the motor
        happens to be right now is considered to be the new 0 position. Useful
        for setting a zero position on a stepper after an initial hardware
        positioning move.

        Has the side effect of setting the current motor speed to 0.

        :param motor_id:  0 - 7

        :param position: Position in steps. This is a 32 bit value
        """

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_current_position: Invalid motor_id.')
        position_bytes = list(position.to_bytes(4, 'big',  signed=True))

        command = [PrivateConstants.STEPPER_SET_CURRENT_POSITION, motor_id]
        for value in position_bytes:
            command.append(value)
        self._send_command(command)

    def stepper_run_speed_to_position(self, motor_id, completion_callback=None):
        """
        Runs the motor at the currently selected speed until the target position is
        reached.

        Does not implement accelerations.

        :param motor_id: 0 - 7

        :param completion_callback: call back function to receive motion complete
                                    notification

        callback returns a data list:

        [report_type, motor_id, raw_time_stamp]

        The report_type = 19
        """
        if not completion_callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_run_speed_to_position: A motion complete '
                               'callback must be '
                               'specified.')
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_run_speed_to_position: Invalid motor_id.')

        self.stepper_info_list[motor_id]['motion_complete_callback'] = completion_callback
        command = [PrivateConstants.STEPPER_RUN_SPEED_TO_POSITION, motor_id]
        self._send_command(command)

    def stepper_stop(self, motor_id):
        """
        Sets a new target position that causes the stepper
        to stop as quickly as possible, using the current speed and
        acceleration parameters.

        :param motor_id:  0 - 7
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_stop: Invalid motor_id.')

        command = [PrivateConstants.STEPPER_STOP, motor_id]
        self._send_command(command)

    def stepper_disable_outputs(self, motor_id):
        """
        Disable motor pin outputs by setting them all LOW.

        Depending on the design of your electronics this may turn off
        the power to the motor coils, saving power.

        This is useful to support Arduino low power modes: disable the outputs
        during sleep and then re-enable with enableOutputs() before stepping
        again.

        If the enable Pin is defined, sets it to OUTPUT mode and clears
        the pin to disabled.

        :param motor_id: 0 - 7
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_disable_outputs: Invalid motor_id.')

        command = [PrivateConstants.STEPPER_DISABLE_OUTPUTS, motor_id]
        self._send_command(command)

    def stepper_enable_outputs(self, motor_id):
        """
        Enable motor pin outputs by setting the motor pins to OUTPUT
        mode.

        If the enable Pin is defined, sets it to OUTPUT mode and sets
        the pin to enabled.

        :param motor_id: 0 - 7
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_enable_outputs: Invalid motor_id.')

        command = [PrivateConstants.STEPPER_ENABLE_OUTPUTS, motor_id]
        self._send_command(command)

    def stepper_set_min_pulse_width(self, motor_id, minimum_width):
        """
        Sets the minimum pulse width allowed by the stepper driver.

        The minimum practical pulse width is approximately 20 microseconds.

        Times less than 20 microseconds will usually result in 20 microseconds or so.

        :param motor_id: 0 - 7

        :param minimum_width: A 16 bit unsigned value expressed in microseconds.
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_min_pulse_width: Invalid motor_id.')

        if not 0 < minimum_width <= 0xff:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_min_pulse_width: Pulse width range = '
                               '0-0xffff.')

        width_msb = minimum_width >> 8
        width_lsb = minimum_width & 0xff

        command = [PrivateConstants.STEPPER_SET_MINIMUM_PULSE_WIDTH, motor_id, width_msb,
                   width_lsb]
        self._send_command(command)

    def stepper_set_enable_pin(self, motor_id, pin=0xff):
        """
        Sets the enable pin number for stepper drivers.
        0xFF indicates unused (default).

        Otherwise, if a pin is set, the pin will be turned on when
        enableOutputs() is called and switched off when disableOutputs()
        is called.

        :param motor_id: 0 - 7
        :param pin: 0-0xff
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_enable_pin: Invalid motor_id.')

        if not 0 < pin <= 0xff:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_enable_pin: Pulse width range = '
                               '0-0xff.')
        command = [PrivateConstants.STEPPER_SET_ENABLE_PIN, motor_id, pin]

        self._send_command(command)

    def stepper_set_3_pins_inverted(self, motor_id, direction=False, step=False,
                                    enable=False):
        """
        Sets the inversion for stepper driver pins.

        :param motor_id: 0 - 7

        :param direction: True=inverted or False

        :param step: True=inverted or False

        :param enable: True=inverted or False
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_3_pins_inverted: Invalid motor_id.')

        command = [PrivateConstants.STEPPER_SET_3_PINS_INVERTED, motor_id, direction,
                   step, enable]

        self._send_command(command)

    def stepper_set_4_pins_inverted(self, motor_id, pin1_invert=False, pin2_invert=False,
                                    pin3_invert=False, pin4_invert=False, enable=False):
        """
        Sets the inversion for 2, 3 and 4 wire stepper pins

        :param motor_id: 0 - 7

        :param pin1_invert: True=inverted or False

        :param pin2_invert: True=inverted or False

        :param pin3_invert: True=inverted or False

        :param pin4_invert: True=inverted or False

        :param enable: True=inverted or False
        """
        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_set_4_pins_inverted: Invalid motor_id.')

        command = [PrivateConstants.STEPPER_SET_4_PINS_INVERTED, motor_id, pin1_invert,
                   pin2_invert, pin3_invert, pin4_invert, enable]

        self._send_command(command)

    def stepper_is_running(self, motor_id, callback):
        """
        Checks to see if the motor is currently running to a target.

        Callback return True if the speed is not zero or not at the target position.

        :param motor_id: 0-7

        :param callback: required callback function to receive report

        :return: The current running state returned via the callback as a list:

        [REPORT_TYPE=18, motor_id, True or False for running state, time_stamp]
        """
        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(
                'stepper_is_running: A callback function must be specified.')

        if not self.stepper_info_list[motor_id]['instance']:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('stepper_is_running: Invalid motor_id.')

        self.stepper_info_list[motor_id]['is_running_callback'] = callback

        command = [PrivateConstants.STEPPER_IS_RUNNING, motor_id]
        self._send_command(command)

    def _set_pin_mode(self, pin_number, pin_state, differential=0, callback=None):
        """
        A private method to set the various pin modes.

        :param pin_number: arduino pin number

        :param pin_state: INPUT/OUTPUT/ANALOG/PWM/PULLUP
                         For SERVO use: set_pin_mode_servo
                         For DHT   use: set_pin_mode_dht

        :param differential: for analog inputs - threshold
                             value to be achieved for report to
                             be generated

        :param callback: A reference to a call back function to be
                         called when pin data value changes

        """
        if callback:
            if pin_state == PrivateConstants.AT_INPUT:
                self.digital_callbacks[pin_number] = callback
            elif pin_state == PrivateConstants.AT_INPUT_PULLUP:
                self.digital_callbacks[pin_number] = callback
            elif pin_state == PrivateConstants.AT_ANALOG:
                self.analog_callbacks[pin_number] = callback
            else:
                print('{} {}'.format('set_pin_mode: callback ignored for '
                                     'pin state:', pin_state))

        if pin_state == PrivateConstants.AT_INPUT:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_INPUT, 1]

        elif pin_state == PrivateConstants.AT_INPUT_PULLUP:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_INPUT_PULLUP, 1]

        elif pin_state == PrivateConstants.AT_OUTPUT:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_OUTPUT]

        elif pin_state == PrivateConstants.AT_ANALOG:
            command = [PrivateConstants.SET_PIN_MODE, pin_number,
                       PrivateConstants.AT_ANALOG,
                       differential >> 8, differential & 0xff, 1]
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('Unknown pin state')

        if command:
            self._send_command(command)

    def shutdown(self):
        """
        This method attempts an orderly shutdown
        If any exceptions are thrown, they are ignored.
        """
        self.shutdown_flag = True

        self._stop_threads()

        try:
            command = [PrivateConstants.STOP_ALL_REPORTS]
            self._send_command(command)
            time.sleep(.5)

            if self.ip_address:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                except Exception:
                    pass
            else:
                try:
                    self.serial_port.reset_input_buffer()
                    self.serial_port.reset_output_buffer()

                    self.serial_port.close()

                except (RuntimeError, SerialException, OSError):
                    # ignore error on shutdown
                    pass
        except Exception:
            raise RuntimeError('Shutdown failed - could not send stop streaming message')

    def sonar_disable(self):
        """
        Disable sonar scanning for all sonar sensors
        """
        command = [PrivateConstants.SONAR_DISABLE]
        self._send_command(command)

    def sonar_enable(self):
        """
        Enable sonar scanning for all sonar sensors
        """
        command = [PrivateConstants.SONAR_ENABLE]
        self._send_command(command)

    def spi_cs_control(self, chip_select_pin, select):
        """
        Control an SPI chip select line
        :param chip_select_pin: pin connected to CS

        :param select: 0=select, 1=deselect
        """
        if not self.spi_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'spi_cs_control: SPI interface is not enabled.')

        if chip_select_pin not in self.cs_pins_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'spi_cs_control: chip select pin never enabled.')
        command = [PrivateConstants.SPI_CS_CONTROL, chip_select_pin, select]
        self._send_command(command)

    def spi_read_blocking(self, register_selection, number_of_bytes_to_read,
                          call_back=None, enable_read_bit=True):
        """
        Read the specified number of bytes from the specified SPI port and
        call the callback function with the reported data.

        :param register_selection: Register to be selected for read.

        :param number_of_bytes_to_read: Number of bytes to read

        :param call_back: Required callback function to report spi data as a
                   result of read command

        :param enable_read_bit: Many SPI devices require that the register
                                selection be OR'ed with 0x80. If set to True
                                the bit will be set.


        callback returns a data list:
        [SPI_READ_REPORT, count of data bytes read, data bytes, time-stamp]

        SPI_READ_REPORT = 13

        """

        if not self.spi_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'spi_read_blocking: SPI interface is not enabled.')

        if not call_back:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('spi_read_blocking: A Callback must be specified')

        self.spi_callback = call_back

        command = [PrivateConstants.SPI_READ_BLOCKING, number_of_bytes_to_read,
                   register_selection, enable_read_bit]

        self._send_command(command)

    def spi_set_format(self, clock_divisor, bit_order, data_mode):
        """
        Configure how the SPI serializes and de-serializes data on the wire.

        See Arduino SPI reference materials for details.

        :param clock_divisor:

        :param bit_order:

                            LSBFIRST = 0

                            MSBFIRST = 1 (default)

        :param data_mode:

                            SPI_MODE0 = 0x00 (default)

                            SPI_MODE1  = 0x04

                            SPI_MODE2 = 0x08

                            SPI_MODE3 = 0x0C

        """

        if not self.spi_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'spi_set_format: SPI interface is not enabled.')

        command = [PrivateConstants.SPI_SET_FORMAT, clock_divisor, bit_order,
                   data_mode]
        self._send_command(command)

    def spi_write_blocking(self, bytes_to_write):
        """
        Write a list of bytes to the SPI device.

        :param bytes_to_write: A list of bytes to write. This must
                                be in the form of a list.

        """

        if not self.spi_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'spi_write_blocking: SPI interface is not enabled.')

        if type(bytes_to_write) is not list:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('spi_write_blocking: bytes_to_write must be a list.')

        command = [PrivateConstants.SPI_WRITE_BLOCKING, len(bytes_to_write)]

        for data in bytes_to_write:
            command.append(data)

        self._send_command(command)

    def set_pin_mode_one_wire(self, pin):
        """
        Initialize the one wire serial bus.

        :param pin: Data pin connected to the OneWire device
        """
        if self.reported_features & PrivateConstants.ONEWIRE_FEATURE:
            self.onewire_enabled = True
            command = [PrivateConstants.ONE_WIRE_INIT, pin]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'The OneWire feature is disabled in the server.')

    def onewire_reset(self, callback=None):
        """
        Reset the onewire device

        :param callback: required  function to report reset result

        callback returns a list:
        [ReportType = 14, Report Subtype = 25, reset result byte,
                        timestamp]
        """
        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_reset: OneWire interface is not enabled.')
        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_reset: A Callback must be specified')

        self.onewire_callback = callback

        command = [PrivateConstants.ONE_WIRE_RESET]
        self._send_command(command)

    def onewire_select(self, device_address):
        """
        Select a device based on its address
        :param device_address: A bytearray of 8 bytes
        """
        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_select: OneWire interface is not enabled.')

        if type(device_address) is not list:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_select: device address must be an array of 8 '
                               'bytes.')

        if len(device_address) != 8:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_select: device address must be an array of 8 '
                               'bytes.')
        command = [PrivateConstants.ONE_WIRE_SELECT]
        for data in device_address:
            command.append(data)
        self._send_command(command)

    def onewire_skip(self):
        """
        Skip the device selection. This only works if you have a
        single device, but you can avoid searching and use this to
        immediately access your device.
        """
        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_skip: OneWire interface is not enabled.')

        command = [PrivateConstants.ONE_WIRE_SKIP]
        self._send_command(command)

    def onewire_write(self, data, power=0):
        """
        Write a byte to the onewire device. If 'power' is one
        then the wire is held high at the end for
        parasitically powered devices. You
        are responsible for eventually de-powering it by calling
        another read or write.

        :param data: byte to write.
        :param power: power control (see above)
        """
        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_write: OneWire interface is not enabled.')
        if 0 < data < 255:
            command = [PrivateConstants.ONE_WIRE_WRITE, data, power]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_write: Data must be no larger than 255')

    def onewire_read(self, callback=None):
        """
        Read a byte from the onewire device
        :param callback: required  function to report onewire data as a
                   result of read command


        callback returns a data list:
        [ONEWIRE_REPORT, ONEWIRE_READ=29, data byte, time-stamp]

        ONEWIRE_REPORT = 14
        """
        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_read: OneWire interface is not enabled.')

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_read A Callback must be specified')

        self.onewire_callback = callback

        command = [PrivateConstants.ONE_WIRE_READ]
        self._send_command(command)

    def onewire_reset_search(self):
        """
        Begin a new search. The next use of search will begin at the first device
        """

        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_reset_search: OneWire interface is not '
                               f'enabled.')
        else:
            command = [PrivateConstants.ONE_WIRE_RESET_SEARCH]
            self._send_command(command)

    def onewire_search(self, callback=None):
        """
        Search for the next device. The device address will returned in the callback.
        If a device is found, the 8 byte address is contained in the callback.
        If no more devices are found, the address returned contains all elements set
        to 0xff.

        :param callback: required  function to report a onewire device address

        callback returns a data list:
        [ONEWIRE_REPORT, ONEWIRE_SEARCH=31, 8 byte address, time-stamp]

        ONEWIRE_REPORT = 14
        """
        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_search: OneWire interface is not enabled.')

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_read A Callback must be specified')

        self.onewire_callback = callback

        command = [PrivateConstants.ONE_WIRE_SEARCH]
        self._send_command(command)

    def onewire_crc8(self, address_list, callback=None):
        """
        Compute a CRC check on an array of data.
        :param address_list:

        :param callback: required  function to report a onewire device address

        callback returns a data list:
        [ONEWIRE_REPORT, ONEWIRE_CRC8=32, CRC, time-stamp]

        ONEWIRE_REPORT = 14

        """

        if not self.onewire_enabled:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'onewire_crc8: OneWire interface is not enabled.')

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_crc8 A Callback must be specified')

        if type(address_list) is not list:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('onewire_crc8: address list must be a list.')

        self.onewire_callback = callback

        address_length = len(address_list)

        command = [PrivateConstants.ONE_WIRE_CRC8, address_length - 1]

        for data in address_list:
            command.append(data)

        self._send_command(command)

    '''
    report message handlers
    '''

    def _analog_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for analog messages.

        :param data: message data

        """
        pin = data[0]
        value = (data[1] << 8) + data[2]
        # set the current value in the pin structure
        time_stamp = time.time()
        # self.digital_pins[pin].event_time = time_stamp
        if self.analog_callbacks[pin]:
            message = [PrivateConstants.ANALOG_REPORT, pin, value, time_stamp]
            self.analog_callbacks[pin](message)

    def _dht_report(self, data):
        """
        This is the dht report handler method.

        :param data:            data[0] = report error return
                                    No Errors = 0

                                    Checksum Error = 1

                                    Timeout Error = 2

                                    Invalid Value = 999

                                data[1] = pin number

                                data[2] = dht type 11 or 22

                                data[3] = humidity positivity flag

                                data[4] = temperature positivity value

                                data[5] = humidity integer

                                data[6] = humidity fractional value

                                data[7] = temperature integer

                                data[8] = temperature fractional value


        """
        if data[0]:  # DHT_ERROR
            # error report
            # data[0] = report sub type, data[1] = pin, data[2] = error message
            if self.dht_callbacks[data[1]]:
                # Callback 0=DHT REPORT, DHT_ERROR, PIN, Time
                message = [PrivateConstants.DHT_REPORT, data[0], data[1], data[2],
                           time.time()]
                self.dht_callbacks[data[1]](message)
        else:
            # got valid data DHT_DATA
            f_humidity = float(data[5] + data[6] / 100)
            if data[3]:
                f_humidity *= -1.0
            f_temperature = float(data[7] + data[8] / 100)
            if data[4]:
                f_temperature *= -1.0
            message = [PrivateConstants.DHT_REPORT, data[0], data[1], data[2],
                       f_humidity, f_temperature, time.time()]

            self.dht_callbacks[data[1]](message)

    def _digital_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for Digital Messages.

        :param data: digital message

        """
        try:
            pin = data[0]
            value = data[1]

            time_stamp = time.time()
            if self.digital_callbacks[pin]:
                message = [PrivateConstants.DIGITAL_REPORT, pin, value, time_stamp]
                self.digital_callbacks[pin](message)
        except:
            print('malformed message in _digital_message')

    def _firmware_message(self, data):
        """
        Telemetrix4Arduino firmware version message

        :param data: data[0] = major number, data[1] = minor number.

                               data[2] = patch number
        """

        self.firmware_version = [data[0], data[1], data[2]]

    def _i2c_read_report(self, data):
        """
        Execute callback for i2c reads.

        :param data: [I2C_READ_REPORT, i2c_port, number of bytes read, address, register, bytes read..., time-stamp]
        """

        # we receive [# data bytes, address, register, data bytes]
        # number of bytes of data returned

        # data[0] = number of bytes
        # data[1] = i2c_port
        # data[2] = number of bytes returned
        # data[3] = address
        # data[4] = register
        # data[5] ... all the data bytes

        cb_list = [PrivateConstants.I2C_READ_REPORT, data[0], data[1]] + data[2:]
        cb_list.append(time.time())

        if cb_list[1]:
            self.i2c_callback2(cb_list)
        else:
            self.i2c_callback(cb_list)

    def _i2c_too_few(self, data):
        """
        I2c reports too few bytes received

        :param data: data[0] = device address
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'i2c too few bytes received from i2c port {data[0]} i2c address {data[1]}')

    def _i2c_too_many(self, data):
        """
        I2c reports too few bytes received

        :param data: data[0] = device address
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'i2c too many bytes received from i2c port {data[0]} i2c address {data[1]}')

    def _i_am_here(self, data):
        """
        Reply to are_u_there message
        :param data: arduino id
        """
        self.reported_arduino_id = data[0]

    def _spi_report(self, report):

        cb_list = [PrivateConstants.SPI_REPORT, report[0]] + report[1:]

        cb_list.append(time.time())

        self.spi_callback(cb_list)

    def _onewire_report(self, report):
        cb_list = [PrivateConstants.ONE_WIRE_REPORT, report[0]] + report[1:]
        cb_list.append(time.time())
        self.onewire_callback(cb_list)

    def _report_debug_data(self, data):
        """
        Print debug data sent from Arduino
        :param data: data[0] is a byte followed by 2
                     bytes that comprise an integer
        :return:
        """
        value = (data[1] << 8) + data[2]
        print(f'DEBUG ID: {data[0]} Value: {value}')

    def _report_loop_data(self, data):
        """
        Print data that was looped back
        :param data: byte of loop back data
        :return:
        """
        if self.loop_back_callback:
            self.loop_back_callback(data)

    def _send_command(self, command):
        """
        This is a private utility method.


        :param command:  command data in the form of a list

        """
        # the length of the list is added at the head
        command.insert(0, len(command))
        send_message = bytes(command)

        if self.serial_port:
            try:
                self.serial_port.write(send_message)
            except SerialException:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('write fail in _send_command')
        elif self.ip_address:
            self.sock.sendall(send_message)
        else:
            raise RuntimeError('No serial port or ip address set.')

    def _servo_unavailable(self, report):
        """
        Message if no servos are available for use.
        :param report: pin number
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(
            f'Servo Attach For Pin {report[0]} Failed: No Available Servos')

    def _sonar_distance_report(self, report):
        """

        :param report: data[0] = trigger pin, data[1] and data[2] = distance

        callback report format: [PrivateConstants.SONAR_DISTANCE, trigger_pin, distance_value, time_stamp]
        """

        # get callback from pin number
        cb = self.sonar_callbacks[report[0]]

        # build report data
        cb_list = [PrivateConstants.SONAR_DISTANCE, report[0],
                   ((report[1] << 8) + report[2]), time.time()]

        cb(cb_list)

    def _stepper_distance_to_go_report(self, report):
        """
        Report stepper distance to go.

        :param report: data[0] = motor_id, data[1] = steps MSB, data[2] = steps byte 1,
                                 data[3] = steps bytes 2, data[4] = steps LSB

        callback report format: [PrivateConstants.STEPPER_DISTANCE_TO_GO, motor_id
                                 steps, time_stamp]
        """

        # get callback
        cb = self.stepper_info_list[report[0]]['distance_to_go_callback']

        # isolate the steps bytes and covert list to bytes
        steps = bytes(report[1:])

        # get value from steps
        num_steps = int.from_bytes(steps, byteorder='big', signed=True)

        cb_list = [PrivateConstants.STEPPER_DISTANCE_TO_GO, report[0], num_steps,
                   time.time()]

        cb(cb_list)

    def _stepper_target_position_report(self, report):
        """
        Report stepper target position to go.

        :param report: data[0] = motor_id, data[1] = target position MSB,
                       data[2] = target position byte MSB+1
                       data[3] = target position byte MSB+2
                       data[4] = target position LSB

        callback report format: [PrivateConstants.STEPPER_TARGET_POSITION, motor_id
                                 target_position, time_stamp]
        """

        # get callback
        cb = self.stepper_info_list[report[0]]['target_position_callback']

        # isolate the steps bytes and covert list to bytes
        target = bytes(report[1:])

        # get value from steps
        target_position = int.from_bytes(target, byteorder='big', signed=True)

        cb_list = [PrivateConstants.STEPPER_TARGET_POSITION, report[0], target_position,
                   time.time()]

        cb(cb_list)

    def _stepper_current_position_report(self, report):
        """
        Report stepper current position.

        :param report: data[0] = motor_id, data[1] = current position MSB,
                       data[2] = current position byte MSB+1
                       data[3] = current position byte MSB+2
                       data[4] = current position LSB

        callback report format: [PrivateConstants.STEPPER_CURRENT_POSITION, motor_id
                                 current_position, time_stamp]
        """

        # get callback
        cb = self.stepper_info_list[report[0]]['current_position_callback']

        # isolate the steps bytes and covert list to bytes
        position = bytes(report[1:])

        # get value from steps
        current_position = int.from_bytes(position, byteorder='big', signed=True)

        cb_list = [PrivateConstants.STEPPER_CURRENT_POSITION, report[0], current_position,
                   time.time()]

        cb(cb_list)

    def _stepper_is_running_report(self, report):
        """
        Report if the motor is currently running

        :param report: data[0] = motor_id, True if motor is running or False if it is not.

        callback report format: [18, motor_id,
                                 running_state, time_stamp]
        """

        # get callback
        cb = self.stepper_info_list[report[0]]['is_running_callback']

        cb_list = [PrivateConstants.STEPPER_RUNNING_REPORT, report[0], time.time()]

        cb(cb_list)

    def _stepper_run_complete_report(self, report):
        """
        The motor completed it motion

        :param report: data[0] = motor_id

        callback report format: [PrivateConstants.STEPPER_RUN_COMPLETE_REPORT, motor_id,
                                 time_stamp]
        """

        # get callback
        cb = self.stepper_info_list[report[0]]['motion_complete_callback']

        cb_list = [PrivateConstants.STEPPER_RUN_COMPLETE_REPORT, report[0],
                   time.time()]

        cb(cb_list)

    def _features_report(self, report):
        self.reported_features = report[0]

    def _run_threads(self):
        self.run_event.set()

    def _is_running(self):
        return self.run_event.is_set()

    def _stop_threads(self):
        self.run_event.clear()

    def _reporter(self):
        """
        This is the reporter thread. It continuously pulls data from
        the deque. When a full message is detected, that message is
        processed.
        """
        self.run_event.wait()

        while self._is_running() and not self.shutdown_flag:
            if len(self.the_deque):
                # response_data will be populated with the received data for the report
                response_data = []
                packet_length = self.the_deque.popleft()
                if packet_length:
                    # get all the data for the report and place it into response_data
                    for i in range(packet_length):
                        while not len(self.the_deque):
                            time.sleep(self.sleep_tune)
                        data = self.the_deque.popleft()
                        response_data.append(data)

                    # print(response_data)

                    # get the report type and look up its dispatch method
                    # here we pop the report type off of response_data
                    report_type = response_data.pop(0)
                    # print(report_type)

                    # retrieve the report handler from the dispatch table
                    dispatch_entry = self.report_dispatch.get(report_type)

                    # if there is additional data for the report,
                    # it will be contained in response_data
                    # noinspection PyArgumentList
                    dispatch_entry(response_data)
                    continue
                else:
                    if self.shutdown_on_exception:
                        self.shutdown()
                    raise RuntimeError(
                        'A report with a packet length of zero was received.')
            else:
                time.sleep(self.sleep_tune)

    def _serial_receiver(self):
        """
        Thread to continuously check for incoming data.
        When a byte comes in, place it onto the deque.
        """
        self.run_event.wait()

        # Don't start this thread if using a tcp/ip transport
        if self.ip_address:
            return

        while self._is_running() and not self.shutdown_flag:
            # we can get an OSError: [Errno9] Bad file descriptor when shutting down
            # just ignore it
            try:
                if self.serial_port.inWaiting():
                    c = self.serial_port.read()
                    self.the_deque.append(ord(c))
                    # print(ord(c))
                else:
                    time.sleep(self.sleep_tune)
                    # continue
            except OSError:
                pass

    def _tcp_receiver(self):
        """
        Thread to continuously check for incoming data.
        When a byte comes in, place it onto the deque.
        """
        self.run_event.wait()

        # Start this thread only if ip_address is set

        if self.ip_address:

            while self._is_running() and not self.shutdown_flag:
                try:
                    payload = self.sock.recv(1)
                    self.the_deque.append(ord(payload))
                except Exception:
                    pass
        else:
            return
