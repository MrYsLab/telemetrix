

<div style="text-align:center;color:#990033; font-family:times, serif; font-size:3.5em"><i>Telemetrix</i></div>
<div style="text-align:center;color:#990033; font-family:times, serif; font-size:2em"><i>The Extensible Alternative To Arduino Firmata</i></div>
<br>

# What Is Telemetry?
*Telemetry* is the process of collecting measurements or other data at remote points and then
automatically transmitting that data to receiving equipment (telecommunication) for monitoring.

<br>

# What is Telemetrix? 

The [Telemetrix Project](https://github.com/MrYsLab/telemetrix) is a Python-based telemetry package for Arduino Core devices 
supporting a serial interface. Telemetrix allows you to develop Python applications that both control and monitor
Arduino Core devices. It was designed to be extensible so that you may easily
add functionality to support an Arduino library of your choice.

<br>


# What is Telemetrix-AIO?

[Telemetrix-AIO](https://github.com/MrYsLab/telemetrix-aio) is a Python 
asyncio version of the Telemetrix client for users who wish to implement their application
using Python's asyncio library.  

<br>

# Summary Of Major Features

* Applications are programmed using conventional Python 3.
* All Data change events are reported using callback functions for asynchronous notification. 
* Each data change event is time-stamped and stored.
* Online [API Reference Documentation for Telemetrix](https://htmlpreview.github.com/?https://github.com/MrYsLab/telemetrix/blob/master/html/telemetrix/index.html).
* Online [API Reference Documentation for Telemetrix-AIO](https://htmlpreview.github.com/?https://github.com/MrYsLab/telemetrix-aio/blob/master/html/telemetrix_aio/index.html).
* A full set of working examples for [Telemetrix](https://github.com/MrYsLab/telemetrix/tree/master/examples) and [Telemetrix-AIO](https://github.com/MrYsLab/telemetrix-aio/tree/master/examples)
are available for download [online.](https://github.com/MrYsLab/pymata4/tree/master/examples)
* Both share a common Arduino Sketch, Telemetrix4Arduino.
* Integrated debugging methods to aid when adding new features.

## Intuitive And Easy To use APIs

For example, to receive asynchronous digital pin state data change notifications, you simply do the following:

1. Set a pin mode for the pin and register a callback function.
2. Have your application sit in a loop waiting for notifications.
    
When either Telemetrix or Telemetrix-AIO executes your callback method, the data parameter will contain
a list of items that describe the change event, including a time-stamp.

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


## What You Will Find In This Document

* Installation and system requirements:
    * [Verifying The Python 3 Version.](./python_3_verify/#how-to-verify-the-python-3-version-installed) 
    * [Python 3 Installation Instructions.](./python_install/#installing-python-37-or-greater)
    * [Installing _telemtrix_ or _telemetrix-aio_.](./install_pymata4/#before-you-install)
    * [Installing the Telemetrix4Arduino sketch.](./firmata_express/#installation-instructions)
* A discussion of the API methods, including links to working examples.
* A tutorial on how to extend Telemetrix and Telemetrix-AIO using
the [DHTNew](https://github.com/RobTillaart/DHTNew) library for DHT type temperature sensors.


<br>
<br>

Copyright (C) 2020 Alan Yorinks. All Rights Reserved.

**Last updated 24 October 2020 **

