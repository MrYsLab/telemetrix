# The Telemetrix and TelemetrixAIO Classes

For the most part, these classes share a common API. Any differences are discussed
in this section. 

To use either of these classes, you must first import it:

##  Telemetrix

### Importing Telemetrix

```python
from telemetrix import telemetrix
```

### Instantiating Telemetrix

```python
board = telemetrix.Telemetrix()
```

## TelemetrixAIO

### Importing TelemetrixAIO

```python
from telemetrix_aio import telemetrix_aio
```

### Instantiating TelemetrixAIO

```python
board = telemetrix_aio.TelemetrixAIO()
```

The *board* variable shown in both examples above contains a reference to the class instance. The
instance variable is used to access any of the API methods for the class.

For example, to cleanly shutdown your Telemetrix or TelemetrixAIO application, call
the *shutdown* method as shown below:

```python
board.shutdown()
```

Of course, you can name the instance variable, anything that is meaningful to you.
There is nothing *magic* about the name *board*.


## Understanding The Telemetrix *\__init__* Parameters
```python
def __init__(self, com_port=None, arduino_instance_id=1,
                 arduino_wait=4, sleep_tune=0.000001,
                 shutdown_on_exception=True,
                 ip_address=None, ip_port=31335):
```
There are several optional parameters available to instantiate the Telemetrix class.
Typically, one accepts all the default values. However, there are times when you may wish 
to take advantage of the flexibility provided
by the \__init__ method parameters, so let's explore the definition and purpose
of each parameter:

### com_port
The *com_port* parameter specifies a serial com_port, such as COM4 or '/dev/ttyACM0'
 used for PC to Arduino communication. If the default value of _None_ is accepted,
 telemetrix will attempt to find the connected Arduino automatically.

### arduino_instance_id
 This parameter
allows telemetrix to connect to an Arduino with a matching ID and 
is useful if you have multiple Arduino's plugged into your computer
and you wish to have a specific Arduino selected by the application for connection.

The default value for the arduino_instance_id for both telemetrix and Telemetrix4Arduino is 1.

Instructions for changing the Telemetrix4Arduino value may be found
in the [**Installing Telemetrix4Arduino**](./telemetrix4arduino.md) section of this document.

### arduino_wait
This parameter specifies the amount of time that Telemetrix assumes it takes for an 
Arduino 
to reboot the Telemetrix4Arduino sketch from a power-up or reset.

The default is 4 seconds. If the Arduino is not fully booted when com_port auto-discovery begins,
auto-discovery will fail.

### sleep_tune
This parameter is the sleep value expressed in seconds that is used at several strategic
points in telemetrix. For example, the serial receiver continuously checks the serial port receive
buffer for an available
character to process. If there is no character in the
buffer, telemetrix sleeps for the sleep_tune period before checking again.

The default value is 0.000001 seconds.

### shutdown_on_exception
When this parameter is set to True, the shutdown method is automatically
called when an exception is detected, and all reporting is disabled.

By setting this parameter to False, the Arduino may continue to send data to
your application even after restarting it.

The default is True and recommended to be used.

### ip_address
When using a WiFi connection to your device, you must specify the IP address of the device. 
If you are using a NodeMCU type device, you can determine the IP address the device is using by 
connecting a serial terminal set to 115200 baud to the USB connector. When a 
connection to the router is complete, the IP address of the device is printed to the terminal console, for example:

```
Connected to WiFi. IP Address: 192.168.2.220  IP Port: 31335
```

### ip_port
The IP port used for the WiFi connection is specified with this parameter. The default is 31335.


## Understanding The TelemetrixAIO *\__init__* Parameters
```python
def __init__(self, com_port=None,
                 arduino_instance_id=1, arduino_wait=4,
                 sleep_tune=0.0001, autostart=True,
                 loop=None, shutdown_on_exception=True,
                 close_loop_on_shutdown=True,
                 ):
        """
        
```
There are several optional parameters available to instantiate the Telemetrix class.
Typically, one accepts all the default values. However, there are times when you may wish 
to take advantage of the flexibility provided
by the \__init__ method parameters, so let's explore the definition and purpose
of each parameter:

### com_port
The *com_port* parameter specifies a serial com_port, such as COM4 or '/dev/ttyACM0'
 used for PC to Arduino communication. If the default value of _None_ is accepted,
 telemetrix_aio will attempt to find the connected Arduino automatically.

### arduino_instance_id
 This parameter
allows telemetrix to connect to an Arduino with a matching ID and 
is useful if you have multiple Arduino's plugged into your computer
and you wish to have a specific Arduino selected by the application for connection.

The default value for the arduino_instance_id for both telemetrix and Telemetrix4Arduino is 1.

Instructions for changing the Telemetrix4Arduino value may be found
in the [**Installing Telemetrix4Arduino**](./telemetrix4arduino.md) section of this document.

### arduino_wait
This parameter specifies the amount of time that Telemetrix assumes it takes for an 
Arduino 
to reboot the Telemetrix4Arduino sketch from a power-up or reset.

The default is 4 seconds. If the Arduino is not fully booted when com_port auto-discovery begins,
auto-discovery will fail.

### sleep_tune
This parameter is the sleep value expressed in seconds that is used at several strategic
points in telemetrix. For example, the serial receiver continuously checks the serial port receive
buffer for an available
character to process. If there is no character in the
buffer, telemetrix_aio sleeps for the sleep_tune period before checking again.

The default value is 0.000001 seconds.

### loop
You may optionally specify a specific ayncio loop to use, or by accepting the
default value of None, the default loop will be assigned for use.

### autostart
When accepting the default value of True, Arduino auto-discovery is performed, and
the report dispatcher task is started.

If your application needs to delay these operations for any reason, set this parameter to
False and then call start_aio to continue with autodiscovery and to start the 
report dispatcher task.


### shutdown_on_exception
When this parameter is set to True, the shutdown method is automatically
called when an exception is detected, and all reporting is disabled.

By setting this parameter to False, the Arduino may continue to send data to
your application even after restarting it.

The default is True and recommended to be used.

### close_loop_on_shutdown
The default for this parameter is True. If True, then when a shutdown occurs,
the asyncio loop will be closed. If you wish to keep the loop active upon a 
telemetrix_aio shutdown, set this parameter to False.

### ip_address

When using a WiFi connection to your device, you must specify the IP address of the device. 
If you are using a NodeMCU type device, you can determine the IP address the device is using
 by connecting a serial terminal set to 115200 baud to the USB connector. When a connection 
to the router is complete, the IP address of the device is printed to the terminal console, for example:

```
Connected to WiFi. IP Address: 192.168.2.220  IP Port: 31335
```

### ip_port
The IP port used for the WiFi connection is specified with this parameter. The default is 31335.

## API Examples

### Telemetrix
   Each [example on GitHub](https://github.com/MrYsLab/telemetrix/tree/master/examples) 
   demonstrates instantiating the Telemetrix class. 
   
   WiFi examples are available
   [here](https://github.com/MrYsLab/telemetrix/tree/master/examples/wifi).
   
### TelemetrixAIO
   Each [example on GitHub](https://github.com/MrYsLab/telemetrix-aio/tree/master/examples) 
   demonstrates instantiating the TelemetrixAIO class. 
   
   WiFi examples are available
   [here](https://github.com/MrYsLab/telemetrix-aio/tree/master/examples/wifi).
   
<br>
<br>

Copyright (C) 2020-21 Alan Yorinks. All Rights Reserved.
