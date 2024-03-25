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

 DHT support courtesy of Martyn Wheeler
 Based on the DHTNew library - https://github.com/RobTillaart/DHTNew

 Modified by Ahto Moorast:
 This example uses two analog read callback methods
 1. cb_analog_input_read_avg()
 Takes 'average_count' amount of samples from a specified pin and returns average value.
 Without currenty knowing how to pass arguments via callback function, the average sample count is controlled via global variables.

 2. cb_analog_input_read_pin()
 Returns a real-time value of the requested pin at request and nothing else. Mutes the callbacks right after.

 NOTE: To measure A15, one must modify Telemetrix4Arduino's MAX_ANALOG_PINS_SUPPORTED to 16 and reflash.
 Because on Mega2560 there's 16x analog pins A0 - A15.
 Line 525: #define MAX_ANALOG_PINS_SUPPORTED 16  //A0 - A15
"""

import sys
import time
import threading
from telemetrix import telemetrix
from matplotlib import pyplot as plot

pinout = {}  # Leave empty
# Dictionary to hold analog pins' raw ADC values.
ADC_results = {
    0: 0,  # pin 0 -> "A0" : 0V
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 0
}
active_pin = None  # pin used for reporting
average_count = 5  # number of samples to average
average_counter = 0  # used in callback

# Digital pins based on Arduino Digital pin numbering.
# When number is used for digital_ functions, the number is according to digital pins.  (13 = D13 != A13)
output_pins = {
    "d_LED": 13,  # Internal LED on MEGA
}

# When number is used for analog_ functions, the number is according to analog pins ??  (13 = A13 != D13)
# Alternatively use the digital pin numberation instead.  54 = D54 = A0
analog_input_pins = {
    "A0": 0,
    "A1": 1,
    "A2": 2,
    "A3": 3,
    "A4": 4,
    "A5": 5,
    "A6": 6,
    "A7": 7,
    "A8": 8,
    "A9": 9,
    "A10": 10,
    "A11": 11,
    "A12": 12,
    "A13": 13,
    "A14": 14,
    "A15": 15,
}

# merge all pins to one dictionary for easier referencing
pinout = analog_input_pins | output_pins

led_state = 1  # for this example

# Using Semitec 103JT-025 10kR NTC Thermistor
R1_temp = 10  # kR


# Mega has 10bits, thus 0 - 1023
def convert_analog(raw_reading: int, Vs: int = 5):
    return (raw_reading * (Vs / 1023))


# def convert_to_temperature(voltage_reading: int):


## ================================================================================================================

# specific class with Telemetrix interface
class Test:
    def __init__(self, com_port=None, arduino_instance_id=1):
        self.board = telemetrix.Telemetrix(com_port, arduino_instance_id)
        self.read_analog_timeout = 3  # in seconds.
        self.cb_flag = 0  # callback filter flag. Only do stuff when requested.

        # Configure pins specific to this example
        self.configure_pins()  # Configure test pin definitions. Assumes pins dictionary is well defined

    # Analog input callback function
    def cb_analog_input_read_avg(self, data):
        if (self.cb_flag):
            global average_count
            global average_counter
            global active_pin

            if (active_pin == data[1]):  # check that the callback is at the desired pin
                if (average_counter > 0):  # if there are still samples to be collected
                    average_counter -= 1
                    # print(f'{average_counter} Value {data[2]}')
                    ADC_results[data[1]] += data[
                        2]  # accumulate the measured value at the corresponding analog pin index
                else:  # calculate the average
                    # print(f'results: {ADC_results[data[1]]} | avg_cnt: {average_count}')
                    ADC_results[data[1]] = ADC_results[data[1]] / average_count
                    # print(f'new results: {ADC_results[data[1]]} | avg_cnt: {average_count}')
                    self.cb_flag = 0  # now reset the flag
        # print(f'Spamming callback from Type: {data[0]} Pin: {data[1]} Value: {data[2]}') # debug

    # Analog input callback function
    def cb_analog_input_read_pin(self, data):
        '''
        This implementation guarantees, only the pin of interest is updated at request.
        :param data: required by Telemetrix
        :return: currently nothing
        '''
        if (
                self.cb_flag == 1):  # Filter. Only act when requested. Otherwise callback is empty and terminates quickly.
            global active_pin  # using global variable...
            if (active_pin == data[1]):  # check that the callback is at the desired pin
                self.cb_flag = 0  # state that the callback has reached
                # print(f'Stored value: Pin Type: {data[0]} Pin: {data[1]} Value: {data[2]}')
                ADC_results[data[1]] = data[
                    2]  # Store the measured value at the corresponding analog pin index
                self.board.disable_analog_reporting(data[1])  # stop callbacks asap
                time.sleep(0.2)
        # print(f'callback Type: {data[0]} Pin: {data[1]} Value: {data[2]}') # debug
        # return data  # not needed at the moment as no way of getting the return from callback ?

    def configure_pins(self):
        # If you set the mode for multiple pins, you may wish to add a short delay after setting each pin.
        # https: // mryslab.github.io / telemetrix / pin_modes /

        # Outputs
        for x in output_pins:  # iterating through outputs to configure them as outputs in Arduino
            self.board.set_pin_mode_digital_output(output_pins[x])
            time.sleep(.02)
        print(f'# Digital output set done')

        '''
        # Analog inputs
        # This seems unnecessary to be done at startup. Since during read_analog, this pretty much repeats per pin.
        # To set up a 'read_all'-like functionality, it would be best to set_pin_mode_analog_input here for all Ax pins
        print("# Setting analog inputs:")
        for x in analog_input_pins:
            # Once pin_mode is set, callbacks are automatically enabled.
            self.board.set_pin_mode_analog_input(analog_input_pins[x], callback=self.cb_analog_input_read_avg)
            time.sleep(.02)
        '''
        self.board.set_analog_scan_interval(200)
        print(f'# Analog input set done')

        self.board.disable_all_reporting()

    def read_analog(self, a_pin_name: str, avg_cnt=5, delay=0.2):
        '''
        :param a_pin_name: string of a pin name written in the dictionary pinout
        :param delay:   default 0 seconds. Time stalled until reading a measurement.
        :param avg_cnt: is only used when cb_analog_input_read_avg() callback is used.
        :return: ([0]return value, [1]return message)
                 [0] - 0-5V - Specific pin's converted value of raw 10bit ADC value;
                 -1 - cb_flag is not reset during timeout
                 -2 - Reading callback not reached - something wrong with calling the callback;
                 [1] "status message")
        '''
        time.sleep(
            delay)  # wait for the delay before reading measurement. use >0.1 when making first measurements.
        pin = pinout[a_pin_name]  # get the pin number from dictionary

        # callback filtering
        global active_pin
        global average_count
        global average_counter
        active_pin = pin  # so that callback can acknowledge the pin under interest
        average_count = avg_cnt
        average_counter = avg_cnt
        self.cb_flag = 1
        ADC_results[pin] = 0  # reset the old measurement

        print(f'# Reading: {a_pin_name}, A{pin}')

        # Setting any analog pin causes callback to be triggered for that pin automatically.
        # self.board.set_pin_mode_analog_input(pin, callback=self.cb_analog_input_read_pin)  # to do single pin reading.
        self.board.set_pin_mode_analog_input(pin,
                                             callback=self.cb_analog_input_read_avg)  # average multiple reads
        time.sleep(0.1)

        time_now = time.time()  # used to do timeout checks.
        while (self.cb_flag == 1):  # callback check. flag is reset in callback.
            if time.time() <= time_now + self.read_analog_timeout:  # implement some timeout
                pass
            else:
                print("analog read timeout")
                return (-1, "analog read timeout")

        if (self.cb_flag == 0):  # check if callback had been reached
            # result is stored in ADC_results dictionary via callback function.
            rslt = convert_analog(ADC_results[pin])
            return (rslt, 'A' + str(pin) + ': ' + str(ADC_results[pin]))
        else:
            print("read_analog callback not reached")
            return (0, "read_analog callback not reached")

    def LED_blink(self, dir_delay: int = 0.5):
        '''
        Call this as a separate Thread !
        :param dir_delay: Time to wait until direction is changed
        :return:
        '''
        global led_state
        time_now = time.time()  # get time when function was called
        while True:  # infinite loop
            if (time.time() > (time_now + dir_delay)):  # When timeout has reached
                time_now = time.time()  # update the start of timer
                self.board.digital_write(pinout["d_LED"], led_state)
                # print(f"Blinking LED {led_state}")
                led_state ^= 1
            pass  # else do nothing


# ===============================================================================================================
# ===============================================================================================================

# Create a Telemetrix instance.
# board = telemetrix.Telemetrix()
test = Test()  # Creates an ServOCP test instance
print(f'# Telemetrix instance creation successful\n')
time.sleep(1)

# background task
print("# LED Blink")
# set 'daemon = True' to terminate function when main program exits.
led = threading.Thread(target=test.LED_blink, args=(0.5,), daemon=True)
led.start()

while True:

    try:
        print("# Read single ADCs")
        print(f'Test acknowledges: {test.read_analog("A15")}')  # A6

        time.sleep(2)
        print("# ADC Result contents")
        print(ADC_results)

        print("# Test script finished")

    except KeyboardInterrupt:
        test.board.shutdown()
        sys.exit(0)

test.board.shutdown()
sys.exit(0)
