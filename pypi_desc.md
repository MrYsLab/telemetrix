# The Telemetrix Project

The Telemetrix Project is a modern-day replacement for 
Arduino StandardFirmata, equipped with many more built-in features than 
StandardFirmata. 

Here is a feature comparison between Telemetrix and StandardFirmata:

| Feature | Telemetrix | StandardFirmata |
|-------|:----------:|:-----------------:|
|     Analog Input    |       X     |      X           |
|     Analog Output (PWM)    |       X     |      X           |
|     Digital Input    |       X     |      X           |
|     Digital Output    |       X     |      X           |
|     i2c Primitives  |       X     |      X           |
|     Servo Motor Control  |       X     |      X           |
|     DHT Temperature/Humidity Sensor  |       X     |                 |
|     OneWire Primitives |       X     |                 |
|     HC-SR04 Sonar Distance Sensor  |       X     |                 |
|     SPI Primitives  |       X     |                 |
|     Stepper Motor Control (AccelStepper) |       X     |                 |
|    Python Threaded Client Included  |       X     |      
|    Python Asyncio Client Included  |       X     |
|    Support For STM32 Boards (Black Pill)|       X     |    
|    Designed To Be User Extensible |       X     |                 |
|    Integrated Debugging Aids Provided |       X     |                 |
|    Examples For All Features |       X     |                 |



The project consists of a 
[Python client API]((https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix/blob/master/html/telemetrix/index.html) )
used to create a Python 
client 
application and C++ servers that communicate with the Python client over a serial or WiFi link. 

This repository is the Python 3 client API.

The server for Arduino serial linked devices is called
[Telemetrix4Arduino](https://github.com/MrYsLab/Telemetrix4Arduino).

The WiFi server for ESP8266 devices is called
[Telemetrix4Esp8266](https://github.com/MrYsLab/Telemetrix4Esp8266).

A [User's Guide](https://mryslab.github.io/telemetrix/) explaining installation and use is available online.

Historically, Telemetrix was developed in phases, and the directories for those phases 
were left 
intact for those interested in the project's beginnings. You may view a discussion of 
these phases on the
[Bots In Pieces](https://mryslab.github.io/bots-in-pieces/arduino,stm32,firmata/2020/09/20/telemetrix-phase-1.html) blog.

