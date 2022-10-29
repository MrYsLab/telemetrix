# Debugging Aids

Because the telemetrix and telemetrix-aio packages utilize serial communication between the client
and the server, it can be difficult to debug the interaction between the two.

Two methods have been provided to aid in debugging.

## loopback
This method allows you to check that there is serial communication between the client and the server.

```python
 def loop_back(self, start_character, callback=None)

    This is a debugging method to send a character to the Arduino device, and have the device loop it back.

    :param start_character: The character to loop back. It should be an integer.

    :param callback: Looped back character will appear in the callback method
```

**Examples:**

1. telemetrix: [loopback.py](https://github.
   com/MrYsLab/telemetrix/blob/master/examples/loop_back.py)
2. telemetrix-aio: [loopback.py](https://github.
   com/MrYsLab/telemetrix-aio/blob/master/examples/loop_back.py)


## send_debug_info reports

There are times when you wish to view values on the Arduino server. There is a C++ function
built into Telemetrix4Arduino, allowing you to send a byte and an integer to be viewed on the
Python console.

```
void send_debug_info(byte id, int value)
```

The report is formatted as follows:

DEBUG ID: _**byte_id**_ Value: **_int_value_**


<br>
<br>

Copyright (C) 2020-21 Alan Yorinks. All Rights Reserved.
