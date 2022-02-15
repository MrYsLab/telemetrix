

<div style="text-align:center;color:#990033; font-family:times, serif; font-size:3.5em"><i>The Telemetrix Project</i></div>
<div style="text-align:center;color:#990033; font-family:times, serif; font-size:2.5em"><i>A User's Guide </i></div>
<br>
<div style="text-align:center;color:#990033; font-family:times, serif;
font-size:2em"><i>Using Telemetrix With Arduino, ESP8266, and STM32 Development Boards </i></div>


<br>


The Telemetrix Project is a modern-day replacement for Arduino StandardFirmata, equipped 
with many more built-in features than StandardFirmata. 
The project consists of Python APIs used to create a Python client application  and C++
servers that communicate with the Python client over a serial or WiFi link. 

The project offers two server libraries to control and monitor a Single Board Computer 
(SBC). [Telemetrix4Arduino](https://github.com/MrYsLab/Telemetrix4Arduino) uses a 
serial USB link, supporting Arduino and STM32 development 
boards, 
and the 
other, [Telemetrix4ESP8266](https://github.com/MrYsLab/Telemetrix4Esp8266), 
uses a WiFi link in support of the ESP-8266.
Both  servers are written using standard Arduino C++ and may be installed 
via the Arduino IDE library manager. Once installed,
no further changes to the SBC code are necessary.

Also included are two client APIs, [_telemetrix_](https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix/blob/master/html/telemetrix/index.html),
which uses standard Python threading 
techniques for concurrency, 
and [_telemetrix-aio_](https://htmlpreview.github.io/?https://github.com/MrYsLab/telemetrix-aio/blob/master/html/telemetrix_aio/index.html) for those who prefer to work 
within a Python asyncio environment. Both clients support serial and WiFi communications 
and may be used with either server.

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



<br>

# Summary Of Major Features

* Applications are programmed using conventional Python 3.
* All Data change events are reported asynchronously via user registered callback 
  functions. Below is the format for all callback functions.
```python
def the_callback(data):
     
            # Your code here
    
```
 When Telemetrix invokes the callback function, the _data_ parameter is populated with 
 a list describing the data change event. For example, for a digital input data change, 
 the list would contain:
 
* A pin-type identifier
* The GPIO PIN Number Identifier
* The reported data change value for the pin
* A time-stamp of when the change occurred.

```python
    [pin_type=digital input, pin_number, pin_value, time stamp]
```
* Intuitive APIs.
    * Online [API Reference Documentation for Telemetrix](https://htmlpreview.github.io/?
   https://github.com/MrYsLab/telemetrix/blob/master/html/telemetrix/index.html).
    * Online [API Reference Documentation for Telemetrix-AIO](https://htmlpreview.github.
   io/?https://github.com/MrYsLab/telemetrix-aio/blob/master/html/telemetrix_aio/index.html).
* A complete set of working examples for [Telemetrix](https://github.
  com/MrYsLab/telemetrix/tree/master/examples) and [Telemetrix-AIO](https://github.com/MrYsLab/telemetrix-aio/tree/master/examples)
are available for download online. WiFi examples are also provided.
* Both clients connect to the servers using a serial or WiFi interface, depending upon 
  the server in use.
* Integrated debugging methods are included to aid in adding new features.

# Working Examples For Digital Input   

Here is a Telemetrix example that monitors digital pin 12 for state changes:

```python
import sys
import time

from telemetrix import telemetrix

"""
Monitor a digital input pin
"""

"""
Setup a pin for digital input and monitor its changes
"""

# Setup a pin for analog input and monitor its changes
DIGITAL_PIN = 12  # arduino pin number

# Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3


def the_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin, current reported value, pin_mode, timestamp]
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    print(f'Pin Mode: {data[CB_PIN_MODE]} Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')


def digital_in(my_board, pin):
    """
     This function establishes the pin as a
     digital input. Any changes on this pin will
     be reported through the call back function.

     :param my_board: a pymata4 instance
     :param pin: Arduino pin number
     """

    # set the pin mode
    my_board.set_pin_mode_digital_input(pin, callback=the_callback)

    print('Enter Control-C to quit.')
    # my_board.enable_digital_reporting(12)
    try:
        while True:
            time.sleep(.0001)
    except KeyboardInterrupt:
        board.shutdown()
        sys.exit(0)


board = telemetrix.Telemetrix()

try:
    digital_in(board, DIGITAL_PIN)
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)

```

And a Telemetrix-AIO version  of the same example:

``` python
import asyncio
import sys
import time

from telemetrix_aio import telemetrix_aio

"""
Monitor a digital input pin
"""

"""
Setup a pin for digital input and monitor its changes
"""

# Setup a pin for analog input and monitor its changes
DIGITAL_PIN = 12  # arduino pin number

# Callback data indices
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3


async def the_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin_mode, pin, current reported value, timestamp]
    """
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
    print(f'Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')


async def digital_in(my_board, pin):
    """
     This function establishes the pin as a
     digital input. Any changes on this pin will
     be reported through the call back function.

     :param my_board: a pymata_express instance
     :param pin: Arduino pin number
     """

    # set the pin mode
    await my_board.set_pin_mode_digital_input(pin, callback=the_callback)

    while True:
        try:
            await asyncio.sleep(.001)
        except KeyboardInterrupt:
            await board.shutdown()
            sys.exit(0)

# get the event loop
loop = asyncio.get_event_loop()

# instantiate pymata_express
board = telemetrix_aio.TelemetrixAIO()

try:
    # start the main function
    loop.run_until_complete(digital_in(board, 12))
except (KeyboardInterrupt, RuntimeError) as e:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)

```

Sample console output as input change events occur:
```bash
Pin: 12 Value: 0 Time Stamp: 2020-03-10 13:26:22
Pin: 12 Value: 1 Time Stamp: 2020-03-10 13:26:27
```



<br>
<br>

Copyright (C) 2020-21 Alan Yorinks. All Rights Reserved.

**Last updated 15 February 2022 **

