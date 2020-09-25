/*
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
 */

#include <Arduino.h>

#define ARDUINO_ID 1
// Pin mode definitions

// INPUT defined in Arduino.h = 0
// OUTPUT defined in Arduino.h = 1
// INPUT_PULLUP defined in Arduino.h = 2
// The following are defined for arduino_telemetrix (AT)
#define AT_ANALOG 3

// the following for future use
#define AT_SERVO 4
#define AT_SONAR 5
#define AT_DHT 6

#define AT_MODE_NOT_SET 255

// Reporting control command - 2 bytes scope and pin
#define REPORTING_DISABLE_ALL 0
#define REPORTING_ANALOG_ENABLE 1
#define REPORTING_DIGITAL_ENABLE 2
#define REPORTING_ANALOG_DISABLE 3
#define REPORTING_DIGITAL_DISABLE 4

// Commands -received by this sketch
#define SERIAL_LOOP_BACK 0
#define SET_PIN_MODE 1
#define DIGITAL_WRITE 2
#define ANALOG_WRITE 3
#define MODIFY_REPORTING 4 // mode(all, analog, or digital), pin, enable or disable
#define GET_FIRMWARE_VERSION 5
#define ARE_U_THERE  6

// this list is a list of the number of bytes for the
// loop, set_pin_mode, digital_write,
// and analog write commands.
// !!!! Important, this list must maintain the order
// of the commands listed above !!!!!
byte command_lengths[] = {1, 4, 2, 2, 1, 0, 0};

// Reports - sent from this sketch
#define DIGITAL_REPORT DIGITAL_WRITE
#define ANALOG_REPORT ANALOG_WRITE
#define FIRMWARE_REPORT 5
#define I_AM_HERE 6
#define DEBUG_PRINT 99

// maximum length of a command in bytes
#define MAX_COMMAND_LENGTH 30

// maximum number of pins supported
#define MAX_DIGITAL_PINS_SUPPORTED 100
#define MAX_ANALOG_PINS_SUPPORTED 15

// firmware version
#define FIRMWARE_MAJOR 0
#define FIRMWARE_MINOR 1


// Analog input pin numbers are defined from
// A0 - A7. Since we do not know if the board
// in use also supports higher analog pin numbers
// we need to define those pin numbers to allow
// the program to compile, even though the
// pins may not exist for the board in use.

#ifndef A8
#define A8 2047
#endif

#ifndef A9
#define A9 2047
#endif

#ifndef A10
#define A10 2047
#endif

#ifndef PIN_A11
#define A11 2047
#endif

#ifndef PIN_A12
#define A12 2047
#endif

#ifndef PIN_A13
#define A13 2047
#endif

#ifndef PIN_A14
#define A14 2047
#endif

#ifndef PIN_A15
#define A15 2047
#endif


// To translate a pin number from an integer value to its analog pin number
// equivalent, this array is used to look up the value to use for the pin.
int analog_read_pins[20] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15};

// a descriptor for digital pins
typedef struct pin_descriptor {
    byte pin_number;
    byte pin_mode;
    bool reporting_enabled;         // If true, then send reports if an input pin
    int last_value;        // Last value read for input mode

};

// an array of digital_pin_descriptors
pin_descriptor the_digital_pins[MAX_DIGITAL_PINS_SUPPORTED];

// an array of analog_pin_descriptors
pin_descriptor the_analog_pins[MAX_ANALOG_PINS_SUPPORTED];


// buffer to hold incoming command data
byte command_buffer[MAX_COMMAND_LENGTH];

unsigned long current_millis;        // for analog input loop
unsigned long previous_millis;       // for analog input loop
unsigned int analog_sampling_interval = 19;

// An array of pointers to the command functions
// Not sure why this needs to be one greater than the actual
// number of commands, but if not this size, the last command fails.
// Will investigate at some later time.
void (*the_commands[7])(void);

// A method to send debug data across the serial link
void send_debug_info(byte id, int value) {
    byte debug_buffer[4] = {DEBUG_PRINT, 0, 0, 0};
    debug_buffer[1] = id;
    debug_buffer[2] = highByte(value);
    debug_buffer[3] = lowByte(value);
    Serial.write(debug_buffer, 4);
}

// command functions
void serial_loopback() {
    Serial.write((byte)SERIAL_LOOP_BACK);
    Serial.write(command_buffer[0]);
}

void set_pin_mode() {
    byte pin;
    byte mode;
    pin = command_buffer[0];
    mode = command_buffer[1];

    // send_debug_info(pin, mode);

    switch (mode) {
        case INPUT:
            the_digital_pins[pin].pin_mode = mode;
            the_digital_pins[pin].reporting_enabled = command_buffer[2];
            pinMode(pin, INPUT);
            break;
        case INPUT_PULLUP:
            the_digital_pins[pin].pin_mode = mode;
            the_digital_pins[pin].reporting_enabled = command_buffer[2];
            pinMode(pin, INPUT_PULLUP);
            break;
        case OUTPUT:
            the_digital_pins[pin].pin_mode = mode;
            pinMode(pin, OUTPUT);
            break;
        case AT_ANALOG:
            the_analog_pins[pin].pin_mode = mode;
            the_analog_pins[pin].reporting_enabled = command_buffer[2];
            // send_debug_info(pin, command_buffer[3]);
            break;
        // the following for future use
        case AT_SERVO:
            // future
            break;
        case AT_SONAR:
            // future
            break;
        case AT_DHT:
            // future
            break;
        default:
            break;
    }
}


void digital_write() {
    byte pin;
    byte value;
    // send_debug_info(99, 99);
    pin = command_buffer[0];
    value = command_buffer[1];
    digitalWrite(pin, value);
}

void analog_write() {
    byte pin;
    byte value;
    // send_debug_info(1, 99);
    pin = command_buffer[0];
    value = command_buffer[1];
    // send_debug_info(pin, value);
    analogWrite(pin, value);
}

void modify_reporting() {
    int pin = command_buffer[1];
    //send_debug_info(6, pin);
    //send_debug_info(7, command_buffer[0]);

    switch (command_buffer[0]) {
        case REPORTING_DISABLE_ALL:
            //send_debug_info(1, command_buffer[0]);
            //send_debug_info(5, 2);
            for (int i = 0; i < MAX_DIGITAL_PINS_SUPPORTED; i++) {
                the_digital_pins[i].reporting_enabled = false;
            }
            for (int i = 0; i < MAX_ANALOG_PINS_SUPPORTED; i++) {
                the_analog_pins[i].reporting_enabled = false;
            }
            //send_debug_info(33,44);
            break;
        case REPORTING_ANALOG_ENABLE:
            if (the_analog_pins[pin].pin_mode != AT_MODE_NOT_SET) {
                the_analog_pins[pin].reporting_enabled = true;
            }
            break;
        case REPORTING_ANALOG_DISABLE:
            if (the_analog_pins[pin].pin_mode != AT_MODE_NOT_SET) {
                the_analog_pins[pin].reporting_enabled = false;
            }
            break;
        case REPORTING_DIGITAL_ENABLE:
            if (the_digital_pins[pin].pin_mode != AT_MODE_NOT_SET) {
                the_digital_pins[pin].reporting_enabled = true;
            }
            break;
        case REPORTING_DIGITAL_DISABLE:
            if (the_digital_pins[pin].pin_mode != AT_MODE_NOT_SET) {
                the_digital_pins[pin].reporting_enabled = false;
            }
            break;
        default:
            break;
    }
}

void get_firmware_version() {
    // send_debug_info(33, 44);
    byte report_message[3] = {FIRMWARE_REPORT, FIRMWARE_MAJOR, FIRMWARE_MINOR};
    Serial.write(report_message, 3);

}

void are_you_there() {
    // send_debug_info(I_AM_HERE, ARDUINO_ID);
    byte report_message[2] = {I_AM_HERE, ARDUINO_ID};
    Serial.write(report_message, 2);


}

void get_next_command() {
    byte command;
    int command_buffer_index = 0;

    for (int i = 0; i < MAX_COMMAND_LENGTH; i++) {
        command_buffer[i] = 0;
    }
    if (Serial.available()) {
        // get the command byte
        command = (byte) Serial.read();
        //send_debug_info(75, command);

        // get the data for that command
        if (command_lengths[command] > 0) {
            for (int i = 0; i < command_lengths[command]; i++) {
                // need this delay or data read is not correct
                // send_debug_info(77, command_lengths[command]);

                delay(1);
                if (Serial.available()) {
                    command_buffer[command_buffer_index++] = (byte) Serial.read();
                    //send_debug_info(3, (int) command_buffer[command_buffer_index - 1]);
                }
                // call the command
                //send_debug_info(76, command);

                (*the_commands[command])();

            }

        } else {
            //send_debug_info(77, command);
            (*the_commands[command])();
        }

    }
}

void scan_digital_inputs() {
    byte value;
    byte input_message[3] = {DIGITAL_REPORT, 0, 0};

    for (int i = 0; i < MAX_DIGITAL_PINS_SUPPORTED; i++) {
        if (the_digital_pins[i].pin_mode == INPUT ||
            the_digital_pins[i].pin_mode == INPUT_PULLUP) {
            // send_debug_info(i, the_digital_pins[i].reporting_enabled);
            if (the_digital_pins[i].reporting_enabled) {
                // if the value changed since last read
                value = (byte) digitalRead(the_digital_pins[i].pin_number);
                // send_debug_info(i, value);
                if (value != the_digital_pins[i].last_value) {
                    the_digital_pins[i].last_value = value;
                    input_message[1] = (byte) i;
                    input_message[2] = value;
                    // send_debug_info(3, value);

                    Serial.write(input_message, 3);
                }
            }
        }
    }
}

void scan_analog_inputs() {
    int value;
    byte input_message[4] = {ANALOG_REPORT, 0, 0, 0};
    uint8_t adjusted_pin_number;

    // send_debug_info(99,99);
    current_millis = millis();
    if (current_millis - previous_millis > analog_sampling_interval) {
        previous_millis += analog_sampling_interval;

        for (int i = 0; i < MAX_ANALOG_PINS_SUPPORTED; i++) {
            if (the_analog_pins[i].pin_mode == AT_ANALOG) {
                if (the_analog_pins[i].reporting_enabled) {
                    // if the value changed since last read
                    // adjust pin number for the actual read
                    adjusted_pin_number = (uint8_t) (analog_read_pins[i]);
                    value = analogRead(adjusted_pin_number);

                    // send_debug_info(i, value);
                    if (value != the_analog_pins[i].last_value) {
                        // check to see if the trigger_threshold was achieved
                        // trigger_value = abs(value - the_analog_pins[i].last_value);

                        // if(trigger_value > the_analog_pins[i].trigger_threshold) {
                        // trigger value achieved, send out the report
                        the_analog_pins[i].last_value = value;
                        // input_message[1] = the_analog_pins[i].pin_number;
                        input_message[1] = (byte) i;
                        input_message[2] = highByte(value); // get high order byte
                        input_message[3] = lowByte(value);
                        Serial.write(input_message, 4);
                        delay(1);
                    }
                }
            }
        }
    }
}

void setup() {
    // create an array of pin_descriptors for 100 pins

    // establish the digital pin array
    for (byte i = 0; i < MAX_DIGITAL_PINS_SUPPORTED; i++) {
        the_digital_pins[i].pin_number = i;
        the_digital_pins[i].pin_mode = AT_MODE_NOT_SET;
        the_digital_pins[i].reporting_enabled = false;
        the_digital_pins[i].last_value = 0;

    }

    // establish the analog pin array
    for (byte i = 0; i < MAX_ANALOG_PINS_SUPPORTED; i++) {
        the_analog_pins[i].pin_number = i;
        the_analog_pins[i].pin_mode = AT_MODE_NOT_SET;
        the_analog_pins[i].reporting_enabled = false;
        the_analog_pins[i].last_value = 0;
    }

    // initialize the function table with pointers to the functions
    the_commands[SERIAL_LOOP_BACK] = serial_loopback;
    the_commands[SET_PIN_MODE] = set_pin_mode;
    the_commands[DIGITAL_WRITE] = digital_write;
    the_commands[ANALOG_WRITE] = analog_write;
    the_commands[MODIFY_REPORTING] = modify_reporting;
    the_commands[GET_FIRMWARE_VERSION] = get_firmware_version;
    the_commands[ARE_U_THERE] = are_you_there;

    Serial.begin(115200);
}

void loop() {
    // keep processing incoming commands
    get_next_command();
    scan_digital_inputs();
    scan_analog_inputs();
}
