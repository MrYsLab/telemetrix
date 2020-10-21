#include <Arduino.h>
#include "Telemetrix4Arduino.h"
#include <Servo.h>
#include <Ultrasonic.h>
#include <Wire.h>
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

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSEf
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */


// We define these here to provide a forward reference.
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

// Phase 3 commands
extern void i2c_begin();

extern void i2c_read();

extern void i2c_write();

extern void sonar_new();


// uncomment out the next line to create a 2nd i2c port
//#define SECOND_I2C_PORT

#ifdef SECOND_I2C_PORT
// Change the pins to match SDA and SCL for your board
#define SECOND_I2C_PORT_SDA PB3
#define SECOND_I2C_PORT_SCL PB10

TwoWire Wire2(SECOND_I2C_PORT_SDA, SECOND_I2C_PORT_SCL);

#endif

// This value must be the same as specified when instantiating the
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
#define I2C_BEGIN 10
#define I2C_READ 11
#define I2C_WRITE 12
#define SONAR_NEW 13

// When adding a new command update the command_table.
// The command length is the number of bytes that follow
// the command byte itself, and does not include the command
// byte in its length.
// The command_func is a pointer the command's function.
typedef struct command_descriptor {
    // a pointer to the command processing function
    void (*command_func)(void);
};

// An array of pointers to the command functions
command_descriptor command_table[15] =
        {
                {&serial_loopback},
                {&set_pin_mode},
                {&digital_write},
                {&analog_write},
                {&modify_reporting},
                {&get_firmware_version},
                {&are_you_there},
                {&servo_attach},
                {&servo_write},
                {&servo_detach},
                {&i2c_begin},
                {&i2c_read},
                {&i2c_write},
                {&sonar_new},
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
#define I2C_TOO_FEW_BYTES_RCVD 8
#define I2C_TOO_MANY_BYTES_RCVD 9
#define I2C_READ_REPORT 10
#define SONAR_DISTANCE 11
#define DEBUG_PRINT 99

// maximum length of a command in bytes
#define MAX_COMMAND_LENGTH 30

// maximum number of pins supported
#define MAX_DIGITAL_PINS_SUPPORTED 100
#define MAX_ANALOG_PINS_SUPPORTED 15

// firmware version
#define FIRMWARE_MAJOR 0
#define FIRMWARE_MINOR 1

// A buffer to hold i2c report data
byte i2c_report_message[64];

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
    bool reporting_enabled; // If true, then send reports if an input pin
    int last_value;        // Last value read for input mode
};

// an array of digital_pin_descriptors
pin_descriptor the_digital_pins[MAX_DIGITAL_PINS_SUPPORTED];

// an array of analog_pin_descriptors
pin_descriptor the_analog_pins[MAX_ANALOG_PINS_SUPPORTED];

unsigned long current_millis;        // for analog input loop
unsigned long previous_millis;       // for analog input loop
unsigned int analog_sampling_interval = 19;

// servo management
Servo servos[MAX_SERVOS];

// this array allows us to retrieve the servo object
// associated with a specific pin number
byte pin_to_servo_index_map[MAX_SERVOS];

// HC-SR04 Sonar Management
#define MAX_SONARS 6

typedef struct Sonar {
    uint8_t trigger_pin;
    int last_value;
    Ultrasonic *usonic;
};

// an array of sonar objects
Sonar sonars[MAX_SONARS];

byte sonars_index = 0; // index into sonars struct

// used for scanning the sonar devices.
byte last_sonar_visited = 0;

unsigned long sonar_current_millis;        // for analog input loop
unsigned long sonar_previous_millis;       // for analog input loop
uint8_t sonar_scan_interval = 33;          // Milliseconds between sensor pings
// (29ms is about the min to avoid = 19;
// buffer to hold incoming command data
byte command_buffer[MAX_COMMAND_LENGTH];

// A method to send debug data across the serial link
void send_debug_info(byte id, int value) {
    byte debug_buffer[5] = {(byte) 4, (byte) DEBUG_PRINT, 0, 0, 0};
    debug_buffer[2] = id;
    debug_buffer[3] = highByte(value);
    debug_buffer[4] = lowByte(value);
    Serial.write(debug_buffer, 5);
}

// command functions
void serial_loopback() {
    byte loop_back_buffer[3] = {2, (byte) SERIAL_LOOP_BACK, command_buffer[0]};
    Serial.write(loop_back_buffer, 3);

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
    byte report_message[4] = {3, FIRMWARE_REPORT, FIRMWARE_MAJOR, FIRMWARE_MINOR};
    Serial.write(report_message, 4);

}

void are_you_there() {
    byte report_message[3] = {2, I_AM_HERE, ARDUINO_ID};
    Serial.write(report_message, 3);
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

    // find the first available open servo
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

/***********************************
 * i2c functions
 **********************************/

/***********************************
 * i2c functions
 **********************************/

void i2c_begin() {
    byte i2c_port = command_buffer[0];
    if (not i2c_port) {
        Wire.begin();
    }

#ifdef SECOND_I2C_PORT
    else{
        Wire2.begin();
    }
#endif
}

void i2c_read() {
    // data in the incoming message:
    // address, [0]
    // register, [1]
    // number of bytes, [2]
    // stop transmitting flag [3]
    // i2c port [4]

    int message_size = 0;
    byte address = command_buffer[0];
    byte the_register = command_buffer[1];

#ifdef SECOND_I2C_PORT
    // this is for port 2
    if(command_buffer[4]){
        Wire2.beginTransmission(address);
        Wire2.write((byte) the_register);
        Wire2.endTransmission(command_buffer[3]); // default = true
        Wire2.requestFrom(address, command_buffer[2]);  // all bytes are returned in requestFrom


        // check to be sure correct number of bytes were returned by slave
        if (command_buffer[2] < Wire2.available()) {
            byte report_message[4] = {3,I2C_TOO_FEW_BYTES_RCVD, 1, address};
            Serial.write(report_message, 4);
            return;

        } else if (command_buffer[2] > Wire2.available()) {
            byte report_message[4] = {3, I2C_TOO_MANY_BYTES_RCVD, 1, address};
            Serial.write(report_message, 4);
            return;
        }
        Wire2.beginTransmission(address);
        Wire2.write((byte) the_register);
        Wire2.endTransmission(command_buffer[3]); // default = true
        Wire2.requestFrom(address, command_buffer[2]);  // all bytes are returned in requestFrom

        // packet length
        i2c_report_message[0] = command_buffer[2] + 5;

        // report type
        i2c_report_message[1] = I2C_READ_REPORT;

        // i2c_port 1 = port 2
        i2c_report_message[2] = 1;

        // number of bytes read
        i2c_report_message[3] = command_buffer[2]; // number of bytes

        // device address
        i2c_report_message[4] = address;

        // device register
        i2c_report_message[5] = the_register;

        // append the data that was read
        for (message_size = 0; message_size < command_buffer[2] && Wire2.available(); message_size++) {
            i2c_report_message[6 + message_size] = Wire2.read();
        }
        // send slave address, register and received bytes
        for (int i = 0; i < message_size + 6; i++) {
            Serial.write(i2c_report_message[i]);
        }
    }
#endif
    // is this for i2c port 0 - default port
    if (not command_buffer[4]) {
        Wire.beginTransmission(address);
        Wire.write((byte) the_register);
        Wire.endTransmission(command_buffer[3]); // default = true
        Wire.requestFrom(address, command_buffer[2]);  // all bytes are returned in requestFrom

        // check to be sure correct number of bytes were returned by slave
        if (command_buffer[2] < Wire.available()) {
            byte report_message[4] = {3,I2C_TOO_FEW_BYTES_RCVD, 0, address};
            Serial.write(report_message, 4);
            return;

        } else if (command_buffer[2] > Wire.available()) {
            byte report_message[4] = {3, I2C_TOO_MANY_BYTES_RCVD, 0, address};
            Serial.write(report_message, 4);
            return;
        }
        Wire.beginTransmission(address);
        Wire.write((byte) the_register);
        Wire.endTransmission(command_buffer[3]); // default = true
        Wire.requestFrom(address, command_buffer[2]);  // all bytes are returned in requestFrom

        // packet length
        i2c_report_message[0] = command_buffer[2] + 5;

        // report type
        i2c_report_message[1] = I2C_READ_REPORT;

        // i2c_port 0 = default
        i2c_report_message[2] = 0;

        // number of bytes read
        i2c_report_message[3] = command_buffer[2]; // number of bytes

        // device address
        i2c_report_message[4] = address;

        // device register
        i2c_report_message[5] = the_register;

        // append the data that was read
        for (message_size = 0; message_size < command_buffer[2] && Wire.available(); message_size++) {
            i2c_report_message[6 + message_size] = Wire.read();
        }
        // send slave address, register and received bytes
        for (int i = 0; i < message_size + 6; i++) {
            Serial.write(i2c_report_message[i]);
        }

    }
}

void i2c_write() {
    // command_buffer[0] is the number of bytes to send
    // command_buffer[1] is the device address
    // command_buffer[2] is the i2c port
    // additional bytes to write= command_buffer[3..];

#ifdef SECOND_I2C_PORT
    // i2c port 2
    if(command_buffer[2]){
        Wire2.beginTransmission(command_buffer[1]);

        // write the data to the device
        for (int i = 0; i < command_buffer[0]; i++) {
            Wire2.write(command_buffer[i + 3]);
        }
    Wire2.endTransmission();
    delayMicroseconds(70);
    }
#endif
    if (not command_buffer[2]) {
        Wire.beginTransmission(command_buffer[1]);

        // write the data to the device
        for (int i = 0; i < command_buffer[0]; i++) {
            Wire.write(command_buffer[i + 3]);
        }
        Wire.endTransmission();
        delayMicroseconds(70);
    }
}


void sonar_new() {
    sonars[sonars_index].usonic = new Ultrasonic((uint8_t) command_buffer[0], (uint8_t) command_buffer[1],
                                                 80000UL);
    sonars[sonars_index].trigger_pin = command_buffer[0];
    sonars_index++;
}


void get_next_command() {
    byte command;
    byte packet_length;
    // int command_buffer_index = 0;
    command_descriptor command_entry;

    memset(command_buffer, 0, sizeof(command_buffer));
    // if there is no command waiting, then return
    if (not Serial.available()) {
        return;
    }
    // get the packet length
    packet_length = (byte) Serial.read();

    while (not Serial.available()) {
        delay(1);
    }

    // get the command byte
    command = (byte) Serial.read();

    // uncomment the next line to see the packet length and command
    //send_debug_info(packet_length, command);
    command_entry = command_table[command];

    if (packet_length > 1) {
        // get the data for that command
        for (int i = 0; i < packet_length - 1; i++) {
            // need this delay or data read is not correct
            while (not Serial.available()) {
                delay(1);
            }
            command_buffer[i] = (byte) Serial.read();
            // uncomment out to see each of the bytes following the command
            //send_debug_info(i, command_buffer[i]);
        }
    }
    command_entry.command_func();
}


void scan_digital_inputs() {
    byte value;
    byte report_message[4] = {3, DIGITAL_REPORT, 0, 0};

    for (int i = 0; i < MAX_DIGITAL_PINS_SUPPORTED; i++) {
        if (the_digital_pins[i].pin_mode == INPUT ||
            the_digital_pins[i].pin_mode == INPUT_PULLUP) {
            if (the_digital_pins[i].reporting_enabled) {
                // if the value changed since last read
                value = (byte) digitalRead(the_digital_pins[i].pin_number);
                if (value != the_digital_pins[i].last_value) {
                    the_digital_pins[i].last_value = value;
                    report_message[2] = (byte) i;
                    report_message[3] = value;
                    Serial.write(report_message, 4);
                }
            }
        }
    }
}

void scan_analog_inputs() {
    int value;
    byte report_message[5] = {4, ANALOG_REPORT, 0, 0, 0};
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
                        report_message[2] = (byte) i;
                        report_message[3] = highByte(value); // get high order byte
                        report_message[4] = lowByte(value);
                        Serial.write(report_message, 5);
                        delay(1);
                    }
                }
            }
        }
    }
}

void scan_sonars() {
    unsigned int distance;

    if (sonars_index) {
        sonar_current_millis = millis();
        if (sonar_current_millis - sonar_previous_millis > sonar_scan_interval) {
            sonar_previous_millis += sonar_scan_interval;
            distance = sonars[last_sonar_visited].usonic->read();
            if (distance != sonars[last_sonar_visited].last_value) {
                sonars[last_sonar_visited].last_value = distance;

                byte report_message[5] = {4, SONAR_DISTANCE, sonars[last_sonar_visited].trigger_pin,
                                          (byte) (distance >> 8), (byte) (distance & 0xff)};
                Serial.write(report_message, 5);
            }
            last_sonar_visited++;
            if (last_sonar_visited == sonars_index) {
                last_sonar_visited = 0;
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
    // initialize the servo allocation map table

    Serial.begin(115200);
}

void loop() {
    // keep processing incoming commands
    get_next_command();
    scan_digital_inputs();
    scan_analog_inputs();
    scan_sonars();

}
