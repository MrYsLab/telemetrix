

<div style="text-align:center;color:#990033; font-family:times, serif; font-size:3.5em"><i>The Telemetrix Project</i></div>
<div style="text-align:center;color:#990033; font-family:times, serif; font-size:2.5em"><i>A User's Guide </i></div>
<br>


*Telemetry* is a system for collecting data on a remote device and then 
automatically transmitting the collected data back to local receiving equipment for processing.

The Telemetrix Project is a telemetry system explicitly designed for Arduino 
Core-based MCUs, using Python on the local client and an Arduino Core 
sketch on the Microcontroller Unit (MCU). Two clients are offered, 
[_telemetrix_](https://github.com/MrYsLab/telemetrix), which uses standard Python threading techniques for concurrency, 
and [_telemetrix-aio_](https://github.com/MrYsLab/telemetrix-aio) for those who prefer to work 
within a Python asyncio environment.

The server, [Telemetrix4Arduino](TBD), is written using standard Arduino C++. It is in an Arduino library format,
but all the operational code is located in a single .ino file, simplifying adding an extension.

Telemetrix was designed with extensibility in mind. Adding new functionality is
straight forward. Debugging tools are integrated into the system aid in extending its functionality.

This guide includes a tutorial explaining the steps taken to add DHT (temperature and humidity) 
sensor support to Telemetrix. The tutorial covers both telemetrix and telemetrix-aio.
<br>

# Summary Of Major Features

* Applications are programmed using conventional Python 3.
* All Data change events are reported asynchronously via user registered callback functions. 
* Each data change event is time-stamped.
* Online [API Reference Documentation for Telemetrix](https://htmlpreview.github.com/?https://github.com/MrYsLab/telemetrix/blob/master/html/telemetrix/index.html).
* Online [API Reference Documentation for Telemetrix-AIO](https://htmlpreview.github.com/?https://github.com/MrYsLab/telemetrix-aio/blob/master/html/telemetrix_aio/index.html).
* A full set of working examples for [Telemetrix](https://github.com/MrYsLab/telemetrix/tree/master/examples) and [Telemetrix-AIO](https://github.com/MrYsLab/telemetrix-aio/tree/master/examples)
are available for download [online.](https://github.com/MrYsLab/pymata4/tree/master/examples)
* Both clients utilize a common Arduino Sketch, _Telemetrix4Arduino_.
* Integrated debugging methods are included to aid in adding new features.

# Intuitive And Easy To use APIs

For example, to receive asynchronous digital pin state data change notifications, you do the following:


* **Set a pin mode for the pin and register an associated callback function for the pin**. 
    Your callback function is written to accept  a single parameter: 
    
        def the_callback(data):
     
            # Your code here
    
    When the telemetrix client calls the callback function, it populates the _data_
parameter with a list describing the data change event.

    For example, for a digital data change, the list would contain the following:
    
    [pin_type=digital input, pin_number, pin_value, time stamp]

    Each input pin type returns a unique list, as described in the API.
    

*  **Have your application sit in a loop waiting for notifications.**
    
# Working Examples    

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

Copyright (C) 2020 Alan Yorinks. All Rights Reserved.

**Last updated 24 October 2020 **

