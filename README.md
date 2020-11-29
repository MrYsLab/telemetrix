# The Telemetrix Project

Telemetry is a system for collecting data on a remote device and then automatically transmitting the 
collected data back to local receiving equipment for processing.

The Telemetrix Project is a telemetry system explicitly designed for Arduino Core-based MCUs, using 
Python on the local client and an 
Arduino Core sketch, called 
[Telemetrix4Arduino](https://github.com/MrYsLab/Telemetrix4Arduino) on the Microcontroller Unit (MCU). 

In addition, WiFi is supported for the ESP8266 when used in conjunction with 
[Telemetrix4Esp8266](https://github.com/MrYsLab/Telemetrix4Esp8266).

It is designed to be user extensible so that you may add support for sensors and actuators
of your choosing.

A [User's Guide](https://mryslab.github.io/telemetrix/) explaining installation and use is available online.

A Python API for may be found [here.](https://htmlpreview.github.com/?https://github.com/MrYsLab/telemetrix/blob/master/html/telemetrix/index.html) 

This project was developed in phases and the directories for those phases were left intact. During the development
phase, the phases were discussed on the 
[Bots In Pieces](https://mryslab.github.io/bots-in-pieces/arduino,stm32,firmata/2020/09/20/telemetrix-phase-1.html) blog.