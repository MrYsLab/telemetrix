#include <Arduino.h>
#include "Telemetrix4Arduino.h"
#include <Servo.h>

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


// We define these here to provide a forward refernce.
// If you add a new command, you must add the command handler
// here as well.

// Phase 1 commands
extern void serial_loopback();

extern void set_pin_mode();

extern void digital_write();

extern void analog_write();

extern void modify_reporting();

extern void get_firmware_version();

extern void are_you_there();

// Phase 2 commands - supporting the servo library
extern void servo_attach();

extern void servo_write();

extern void servo_detach();


// This value must be the same as specified when intantiating the
// telemetrix client. The client defaults to a value of 1.
// This value is used for the client to auto-discover and to
// connect to a specific board regardless of the current com port
// it is currently connected to.
#define ARDUINO_ID 1

// Commands -received by this sketch
// Add commands retaining the sequential numbering.
// The order of commands here must be maintained in the command_table.
#define SERIAL_LOOP_BACK 0
#define SET_PIN_MODE 1
#define DIGITAL_WRITE 2
#define ANALOG_WRITE 3
#define MODIFY_REPORTING 4 // mode(all, analog, or digital), pin, enable or disable
#define GET_FIRMWARE_VERSION 5
#define ARE_U_THERE  6
#define SERVO_ATTACH 7
#define SERVO_WRITE 8
#define SERVO_DETACH 9


// When adding a new command update the command_table.
// The command length is the number of bytes that follow
// the command byte itself, and does not include the command
// byte in its length.
// The command_func is a pointer the command's function.
typedef struct command_descriptor {
    //byte command;
    byte command_length;

    void (*command_func)(void);
};
command_descriptor command_table[12] =

        {
                {1, &serial_loopback},
                {4, &set_pin_mode},
                {2, &digital_write},
                {2, &analog_write},
                {1, &modify_reporting},
                {0, &get_firmware_version},
                {0, &are_you_there},
                {5, &servo_attach},
                {2, &servo_write},
                {1, &servo_detach},
        };

// Input pin reporting control sub commands (modify_reporting)
#define REPORTING_DISABLE_ALL 0
#define REPORTING_ANALOG_ENABLE 1
#define REPORTING_DIGITAL_ENABLE 2
#define REPORTING_ANALOG_DISABLE 3
#define REPORTING_DIGITAL_DISABLE 4

// Pin mode definitions

// INPUT defined in Arduino.h = 0
// OUTPUT defined in Arduino.h = 1
// INPUT_PULLUP defined in Arduino.h = 2
// The following are defined for arduino_telemetrix (AT)
#define AT_ANALOG 3
#define AT_MODE_NOT_SET 255



// Reports - sent from this sketch
#define DIGITAL_REPORT DIGITAL_WRITE
#define ANALOG_REPORT ANALOG_WRITE
#define FIRMWARE_REPORT 5
#define I_AM_HERE 6
#define SERVO_UNAVAILABLE 7
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
    void *sensor_ptr;      // a pointer to be used to store items such as
    // a servo object returned by the library.

};

// servo management
Servo servos[MAX_SERVOS];

//
byte pin_to_servo_index_map[MAX_SERVOS];

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
    Serial.write((byte) SERIAL_LOOP_BACK);
    Serial.write(command_buffer[0]);
}

void set_pin_mode() {
    byte pin;
    byte mode;
    pin = command_buffer[0];
    mode = command_buffer[1];

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
            break;
        default:
            break;
    }
}


void digital_write() {
    byte pin;
    byte value;
    pin = command_buffer[0];
    value = command_buffer[1];
    digitalWrite(pin, value);
}

void analog_write() {
    byte pin;
    byte value;
    pin = command_buffer[0];
    value = command_buffer[1];
    analogWrite(pin, value);
}

void modify_reporting() {
    int pin = command_buffer[1];

    switch (command_buffer[0]) {
        case REPORTING_DISABLE_ALL:
            for (int i = 0; i < MAX_DIGITAL_PINS_SUPPORTED; i++) {
                the_digital_pins[i].reporting_enabled = false;
            }
            for (int i = 0; i < MAX_ANALOG_PINS_SUPPORTED; i++) {
                the_analog_pins[i].reporting_enabled = false;
            }
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
    // (33, 44);
    byte report_message[3] = {FIRMWARE_REPORT, FIRMWARE_MAJOR, FIRMWARE_MINOR};
    Serial.write(report_message, 3);

}

void are_you_there() {
    byte report_message[2] = {I_AM_HERE, ARDUINO_ID};
    Serial.write(report_message, 2);
}


/***************************************************
 * Servo Commands
 **************************************************/

// Find the first servo that is not attached to a pin
int find_servo() {
    int index = -1;
    for (int i = 0; i < MAX_SERVOS; i++) {
        if (servos[i].attached() == false) {
            index = i;
            break;
        }
    }
    return index;
}

void servo_attach() {

    byte pin = command_buffer[0];
    int servo_found = -1;

    int minpulse = (command_buffer[1] << 8) + command_buffer[2];
    int maxpulse = (command_buffer[3] << 8) + command_buffer[4];

    // find the first avalable open servo
    servo_found = find_servo();
    if (servo_found != -1) {
        pin_to_servo_index_map[servo_found] = pin;
        servos[servo_found].attach(pin, minpulse, maxpulse);
    } else {
        // no open servos available, send a report back to client
        byte report_message[2] = {SERVO_UNAVAILABLE, pin};
        Serial.write(report_message, 2);
    }
}

// set a servo to a given angle
void servo_write() {
    byte pin = command_buffer[0];
    int angle = command_buffer[1];
    servos[0].write(angle);
    // find the servo object for the pin
    for (int i = 0; i < MAX_SERVOS; i++) {
        if (pin_to_servo_index_map[i] == pin) {

            servos[i].write(angle);
            return;
        }
    }
}

// detach a servo and make it available for future use
void servo_detach() {
    byte pin = command_buffer[0];

    // find the servo object for the pin
    for (int i = 0; i < MAX_SERVOS; i++) {
        if (pin_to_servo_index_map[i] == pin) {

            pin_to_servo_index_map[i] = -1;
            servos[i].detach();
        }
    }
}

void get_next_command() {
    byte command;
    int command_buffer_index = 0;
    command_descriptor command_entry;

    for (int i = 0; i < MAX_COMMAND_LENGTH; i++) {
        command_buffer[i] = 0;
    }
    if (Serial.available()) {
        // get the command byte
        command = (byte) Serial.read();
        // uncomment the next line to see the command byte value
        //send_debug_info(75, command);
        command_entry = command_table[command];
        //send_debug_info(command, command_entry.command_length);
        // get the data for that command
        if (command_entry.command_length > 0) {
            for (int i = 0; i < command_entry.command_length; i++) {
                // need this delay or data read is not correct
                delay(1);
                if (Serial.available()) {
                    command_buffer[command_buffer_index++] = (byte) Serial.read();
                    // uncomment out to see each of the bytes followning the command
                    //send_debug_info(3, (int) command_buffer[command_buffer_index - 1]);
                }
            }
        }
        (command_entry.command_func());
    }

}

void scan_digital_inputs() {
    byte value;
    byte input_message[3] = {DIGITAL_REPORT, 0, 0};

    for (int i = 0; i < MAX_DIGITAL_PINS_SUPPORTED; i++) {
        if (the_digital_pins[i].pin_mode == INPUT ||
            the_digital_pins[i].pin_mode == INPUT_PULLUP) {
            if (the_digital_pins[i].reporting_enabled) {
                // if the value changed since last read
                value = (byte) digitalRead(the_digital_pins[i].pin_number);
                if (value != the_digital_pins[i].last_value) {
                    the_digital_pins[i].last_value = value;
                    input_message[1] = (byte) i;
                    input_message[2] = value;
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
    //myservo.attach(5);
    //delay(500);
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

    // initialize the servo allocation map table

    Serial.begin(115200);
}

void loop() {
    // keep processing incoming commands
    get_next_command();
    scan_digital_inputs();
    scan_analog_inputs();

}
