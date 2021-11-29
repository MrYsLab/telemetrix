# The Telemetrix Project

The Telemetrix Project is a modern-day replacement for 
Arduino StandardFirmata, but is equipped with many more built-in features than 
StandardFirmata. 

The project consists of Python client API used to create a Python 
client 
application and C++ servers that communicate with the Python client over a serial or WiFi link. 

This repository is the Python 3 client API

The server for Arduino serial linked devices is called
[Telemetrix4Arduino](https://github.com/MrYsLab/Telemetrix4Arduino) 

The WiFi server for ESP8266 devices is called
[Telemetrix4Esp8266](https://github.com/MrYsLab/Telemetrix4Esp8266).

It is designed to be user extensible so that you may add support for sensors and actuators
of your choosing.

A [User's Guide](https://mryslab.github.io/telemetrix/) explaining installation and use is available online.

A Python API for may be found [here.](https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix/blob/master/html/telemetrix/index.html) 

This project was developed in phases, and the directories for those phases were left 
intact. During the development
phase, the phases were discussed on the 
[Bots In Pieces](https://mryslab.github.io/bots-in-pieces/arduino,stm32,firmata/2020/09/20/telemetrix-phase-1.html) blog.

The following functionality is implemented in this release:

* Analog Input
* Digital Input, Digital Input Pullup
* PWM output
* Loopback (for client/server link debugging)
* I2C Support
* SPI Support
* OneWire Support
* Servo Support
* HC-SR04 Type Sonar Distance Sensor Support
* DHT 11 and 22 Humidity/Temperature Sensor Support
* Stepper Motor Support For Up To 4 Motors
