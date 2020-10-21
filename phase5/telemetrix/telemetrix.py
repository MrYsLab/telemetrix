"""
 Copyright (c) 2020 Alan Yorinks All rights reserved.

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
import threading
import time
from collections import deque

import serial
# noinspection PyPackageRequirementscd
from serial.serialutil import SerialException
# noinspection PyPackageRequirements
from serial.tools import list_ports

from telemetrix.private_constants import PrivateConstants


# noinspection PyPep8,PyMethodMayBeStatic
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
                 shutdown_on_exception=True):

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
        """

        # initialize threading parent
        threading.Thread.__init__(self)

        # create the threads and set them as daemons so
        # that they stop when the program is closed

        # create a thread to interpret received serial data
        self.the_reporter_thread = threading.Thread(target=self._reporter)
        self.the_reporter_thread.daemon = True

        self.the_data_receive_thread = threading.Thread(target=self._serial_receiver)

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
        self.report_dispatch.update({PrivateConstants.LOOP_COMMAND: self._report_loop_data})
        self.report_dispatch.update({PrivateConstants.DEBUG_PRINT: self._report_debug_data})
        self.report_dispatch.update({PrivateConstants.DIGITAL_REPORT: self._digital_message})
        self.report_dispatch.update({PrivateConstants.ANALOG_REPORT: self._analog_message})
        self.report_dispatch.update({PrivateConstants.FIRMWARE_REPORT: self._firmware_message})
        self.report_dispatch.update({PrivateConstants.I_AM_HERE_REPORT: self._i_am_here})
        self.report_dispatch.update({PrivateConstants.SERVO_UNAVAILABLE: self._servo_unavailable})
        self.report_dispatch.update({PrivateConstants.I2C_READ_REPORT: self._i2c_read_report})
        self.report_dispatch.update({PrivateConstants.I2C_TOO_FEW_BYTES_RCVD: self._i2c_too_few})
        self.report_dispatch.update({PrivateConstants.I2C_TOO_MANY_BYTES_RCVD: self._i2c_too_many})
        self.report_dispatch.update({PrivateConstants.SONAR_DISTANCE: self._sonar_distance_report})

        # dictionaries to store the callbacks for each pin
        self.analog_callbacks = {}

        self.digital_callbacks = {}

        self.i2c_callback = None
        self.i2c_callback2 = None

        self.i2c_1_active = False
        self.i2c_2_active = False

        # the trigger pin will be the key to retrieve
        # the callback for a specific HC-SR04
        self.sonar_callbacks = {}

        self.sonar_count = 0

        # serial port in use
        self.serial_port = None

        # flag to indicate we are in shutdown mode
        self.shutdown_flag = False

        # debug loopback callback method
        self.loop_back_callback = None

        # flag to indicate the start of a new report
        # self.new_report_start = True

        # firmware version to be stored here
        self.firmware_version = []

        # reported arduino instance id
        self.reported_arduino_id = []

        # flag to indicate if i2c was previously enabled
        self.i2c_enabled = False

        self.the_reporter_thread.start()
        self.the_data_receive_thread.start()

        print(f"Telemetrix:  Version {PrivateConstants.TELEMETRIX_VERSION}\n\n"
              f"Copyright (c) 2020 Alan Yorinks All Rights Reserved.\n")

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
            print(f"Arduino compatible device found and connected to {self.serial_port.port}")

            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

        # no com_port found - raise a runtime exception
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('No Arduino Found or User Aborted Program')

        # allow the threads to run
        self._run_threads()
        print(f'Waiting for Arduino to reset')
        print(f'Reset Complete')

        print('Retrieving Arduino ID...')
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
            raise RuntimeError(f'Telemetrix4Arduino firmware version')

        else:
            print(f'Telemetrix4Arduino firmware version: {self.firmware_version[0]}.'
                  f'{self.firmware_version[1]}')

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
        for port in the_ports_list:
            if port.pid is None:
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
        print(f'\nWaiting {self.arduino_wait} seconds(arduino_wait) for Arduino devices to '
              'reset...')
        # temporary for testing
        time.sleep(self.arduino_wait)

        # check for correct arduino device
        self.serial_port.reset_input_buffer()
        self.serial_port.reset_output_buffer()

    def _manual_open(self):
        """
        Com port was specified by the user - try to open up that port

        """
        # if port is not found, a serial exception will be thrown
        try:
            print(f'Opening {self.com_port}...')
            self.serial_port = serial.Serial(self.com_port, 115200,
                                             timeout=1, writeTimeout=0)

            print(f'\nWaiting {self.arduino_wait} seconds(arduino_wait) for Arduino devices to '
                  'reset...')
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
                raise RuntimeError(f'Telemetrix4Arduino Sketch Firmware Version Not Found')

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

        :param value: pin value (1 or 0)

        """
        command = [PrivateConstants.ANALOG_WRITE, pin, value]
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
        command = [PrivateConstants.MODIFY_REPORTING, PrivateConstants.REPORTING_DISABLE_ALL, 0]
        self._send_command(command)

    def disable_analog_reporting(self, pin):
        """
        Disables analog reporting for a single analog pin.

        :param pin: Analog pin number. For example for A0, the number is 0.

        """
        command = [PrivateConstants.MODIFY_REPORTING, PrivateConstants.REPORTING_ANALOG_DISABLE, pin]
        self._send_command(command)

    def disable_digital_reporting(self, pin):
        """
        Disables digital reporting. By turning reporting off for this pin,
        Reporting is disabled for all 8 bits in the "port"

        :param pin: Pin and all pins for this port

        """
        command = [PrivateConstants.MODIFY_REPORTING, PrivateConstants.REPORTING_DIGITAL_DISABLE, pin]
        self._send_command(command)

    def enable_analog_reporting(self, pin):
        """
        Enables analog reporting. This is an alias for set_pin_mode_analog_input.
        Disabling analog reporting sets the pin to a digital input pin,
        so we need to provide the callback and differential if we wish
        to specify it.

        :param pin: Analog pin number. For example for A0, the number is 0.


        """
        command = [PrivateConstants.MODIFY_REPORTING, PrivateConstants.REPORTING_ANALOG_ENABLE, pin]
        self._send_command(command)

    def enable_digital_reporting(self, pin):
        """
        Enable reporting on the digital pin.

        :param pin: Pin number.
        """

        command = [PrivateConstants.MODIFY_REPORTING, PrivateConstants.REPORTING_DIGITAL_ENABLE, pin]
        self._send_command(command)

    def _get_arduino_id(self):
        """
        Retrieve arduino-telemetrix arduino id

        """
        command = [PrivateConstants.ARE_U_THERE]
        self._send_command(command)
        # provide time for the reply
        time.sleep(.1)

    def _get_firmware_version(self):
        """
        This method retrieves the
        arduino-telemetrix firmware version

        """
        command = [PrivateConstants.GET_FIRMWARE_VERSION]
        self._send_command(command)
        # provide time for the reply
        time.sleep(.1)

    def i2c_read(self, address, register, number_of_bytes,
                 callback=None, i2c_port=0):
        """
        Read the specified number of bytes from the specified register for
        the i2c device.


        :param address: i2c device address

        :param register: i2c register (or None if no register selection is needed)

        :param number_of_bytes: number of bytes to be read

        :param callback: Required callback function to report i2c data as a
                   result of read command


        callback returns a data list:
        [I2C_READ_REPORT, address, register, count of data bytes, data bytes, time-stamp]

        """

        self._i2c_read_request(address, register, number_of_bytes,
                               callback=callback, i2c_port=i2c_port)

    def i2c_read_restart_transmission(self, address, register,
                                      number_of_bytes,
                                      callback=None, i2c_port=0):
        """
        Read the specified number of bytes from the specified register for
        the i2c device. This restarts the transmission after the read. It is
        required for some i2c devices such as the MMA8452Q accelerometer.


        :param address: i2c device address

        :param register: i2c register (or None if no register
                                                    selection is needed)

        :param number_of_bytes: number of bytes to be read

        :param callback: Required callback function to report i2c data as a
                   result of read command


        callback returns a data list:

        [I2C_READ_REPORT, address, register, count of data bytes, data bytes, time-stamp]

        """

        self._i2c_read_request(address, register, number_of_bytes, stop_transmission=False,
                               callback=callback, i2c_port=i2c_port)

    def _i2c_read_request(self, address, register, number_of_bytes,
                          stop_transmission=True, callback=None, i2c_port=0):
        """
        This method requests the read of an i2c device. Results are retrieved
        via callback.

        :param address: i2c device address

        :param register: register number (or None if no register selection is needed)

        :param number_of_bytes: number of bytes expected to be returned

        :param stop_transmission: stop transmission after read

        :param callback: Required callback function to report i2c data as a
                   result of read command.

        """
        if not i2c_port:
            if not self.i2c_1_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('I2C Read: set_pin_mode i2c never called for i2c port 1.')

        if i2c_port:
            if not self.i2c_2_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('I2C Read: set_pin_mode i2c never called for i2c port 2.')

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

        # message contains:
        # 1. address
        # 2. register
        # 3. number of bytes
        # 4. restart_transmission - True or False
        # 5. i2c port

        command = [PrivateConstants.I2C_READ, address, register, number_of_bytes,
                   stop_transmission, i2c_port]
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
                raise RuntimeError('I2C Write: set_pin_mode i2c never called for i2c port 1.')

        if i2c_port:
            if not self.i2c_2_active:
                if self.shutdown_on_exception:
                    self.shutdown()
                raise RuntimeError('I2C Write: set_pin_mode i2c never called for i2c port 2.')

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

    def set_pin_mode_analog_output(self, pin_number):
        """
        Set a pin as a pwm (analog output) pin.

        :param pin_number:arduino pin number

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_OUTPUT)

    def set_pin_mode_analog_input(self, pin_number, callback=None):
        """
        Set a pin as an analog input.

        :param pin_number: arduino pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for analog input pins = 2

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_ANALOG,
                           callback=callback)

    def set_pin_mode_digital_input(self, pin_number, callback=None):
        """
        Set a pin as a digital input.

        :param pin_number: arduino pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for digital input pins = 0

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT, callback)

    def set_pin_mode_digital_input_pullup(self, pin_number, callback=None):
        """
        Set a pin as a digital input with pullup enabled.

        :param pin_number: arduino pin number

        :param callback: callback function


        callback returns a data list:

        [pin_type, pin_number, pin_value, raw_time_stamp]

        The pin_type for digital input pins with pullups enabled = 11

        """
        self._set_pin_mode(pin_number, PrivateConstants.AT_INPUT_PULLUP, callback)

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

    def set_pin_mode_servo(self, pin_number, min_pulse=544, max_pulse=2400):
        """

        Attach a pin to a servo motor

        :param pin_number: pin

        :param min_pulse: minimum pulse width

        :param max_pulse: maximum pulse width

        """
        minv = (min_pulse).to_bytes(2, byteorder="big")
        maxv = (max_pulse).to_bytes(2, byteorder="big")

        command = [PrivateConstants.SERVO_ATTACH, pin_number,
                   minv[0], minv[1], maxv[0], maxv[1]]
        self._send_command(command)

    def set_pin_mode_sonar(self, trigger_pin, echo_pin,
                           callback=None):
        """

        :param trigger_pin:

        :param echo_pin:

        :param callback: All sonars share a single callback

        """

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
            raise RuntimeError(f'Maximum Number Of Sonars Exceeded - set_pin_mode_sonar fails for pin {trigger_pin}')

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

    def _set_pin_mode(self, pin_number, pin_state, callback=None):

        """
        A private method to set the various pin modes.

        :param pin_number: arduino pin number

        :param pin_state: INPUT/OUTPUT/ANALOG/PWM/PULLUP
                         For SERVO use: set_pin_mode_servo
                         For DHT   use: set_pin_mode_dht

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
            command = [PrivateConstants.SET_PIN_MODE, pin_number, PrivateConstants.AT_INPUT, 1]

        elif pin_state == PrivateConstants.AT_INPUT_PULLUP:
            command = [PrivateConstants.SET_PIN_MODE, pin_number, PrivateConstants.AT_INPUT_PULLUP, 1]

        elif pin_state == PrivateConstants.AT_OUTPUT:
            command = [PrivateConstants.SET_PIN_MODE, pin_number, PrivateConstants.AT_OUTPUT]

        elif pin_state == PrivateConstants.AT_ANALOG:
            command = [PrivateConstants.SET_PIN_MODE, pin_number, PrivateConstants.AT_ANALOG, 1]
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
            self.disable_all_reporting()

            self.serial_port.reset_input_buffer()
            self.serial_port.close()

        except (RuntimeError, SerialException, OSError):
            # ignore error on shutdown
            pass

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

    def _digital_message(self, data):
        """
        This is a private message handler method.
        It is a message handler for Digital Messages.

        :param data: digital message

        """
        pin = data[0]
        value = data[1]

        time_stamp = time.time()
        if self.digital_callbacks[pin]:
            message = [PrivateConstants.DIGITAL_REPORT, pin, value, time_stamp]
            self.digital_callbacks[pin](message)

    def _firmware_message(self, data):
        """
        Telemetrix4Arduino firmware version message
        :param data: data[0] = major number, data[1] = minor number
        """

        self.firmware_version = [data[0], data[1]]

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
        raise RuntimeError(f'i2c too few bytes received from i2c port {data[0]} i2c address {data[1]}')

    def _i2c_too_many(self, data):
        """
        I2c reports too few bytes received

        :param data: data[0] = device address
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(f'i2c too many bytes received from i2c port {data[0]} i2c address {data[1]}')

    def _i_am_here(self, data):
        """
        Reply to are_u_there message
        :param data: arduino id
        """
        self.reported_arduino_id = data[0]

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

        :returns: number of bytes sent
        """
        # the length of the list is added at the head
        command.insert(0, len(command))
        # print(command)
        send_message = bytes(command)
        try:
            self.serial_port.write(send_message)
            # print(send_message)
        except SerialException:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('write fail in _send_command')

    def _servo_unavailable(self, report):
        """
        Message if no servos are available for use.
        :param report: pin number
        """
        if self.shutdown_on_exception:
            self.shutdown()
        raise RuntimeError(f'Servo Attach For Pin {report[0]} Failed: No Available Servos')

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
        num_args = 0
        method = None

        while self._is_running() and not self.shutdown_flag:
            if len(self.the_deque):
                # response_data will be populated with the received data for the report
                response_data = []
                packet_length = self.the_deque.popleft()
                if packet_length:
                    # get all the data for the report and place it into response_data
                    for i in range(packet_length):
                        while not len(self.the_deque):
                        # while len(self.the_deque) < packet_length:
                           time.sleep(self.sleep_tune)
                        data = self.the_deque.popleft()
                        response_data.append(data)

                    # get the report type and look up its dispatch method
                    # here we pop the report type off of response_data
                    report_type = response_data.pop(0)

                    # retrieve the report handler from the dispatch table
                    dispatch_entry = self.report_dispatch.get(report_type)

                    # if there is additional data for the report,
                    # it will be contained in response_data
                    dispatch_entry(response_data)
                    continue

                else:
                    if self.shutdown_on_exception:
                        self.shutdown()
                    raise RuntimeError('A report with a packet length of zero was received.')
            else:
                time.sleep(self.sleep_tune)

    def _serial_receiver(self):
        """
        Thread to continuously check for incoming data.
        When a byte comes in, place it onto the deque.
        """
        self.run_event.wait()

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
