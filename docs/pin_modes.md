# Introduction
A pin on an Arduino-core device can be configured to operate in one of several modes.

For example, 
a digital pin may be configured for input, output, and some digital pins may be 
used for analog output (PWM) operation.

Analog input pins
are even more flexible.
They may be configured for analog input, digital input, or digital output operation.

#### Mapping Analog Pin Numbers To Digital Pin Numbers
When configuring an analog input pin as a digital input, you must use the pin's digital pin number equivalent. 
For example, if you wish to use pin A0 as a digital pin on an Arduino Uno, 
the digital pin number equivalent is 14.  In general, to find the digital equivalent of pin A0 for your specific
Arduino board type, the algorithm is:

digital_pin_number = analog_pin_number + number of digital pins

Looking at the Uno:
A0 = 14, A1 = 15, and so forth.

Looking at a Mega2560 which has 54 digital pins:
A0 = 54, A1 = 55, etc.

However, this not always the case, so please consult the documentation for the board in use.

Both telemetrix and telemetrix-aio require that a pin's 
mode be explicitly set by calling one of the mode-setting methods before using a pin.


In this section, the methods to set pin modes are presented. For each API method, a link to an example is
provided. The API parameters for both telemetrix and telemetrix-aio are identical for setting pin modes, except
telemetrix-aio method definitions are prefixed with the Python _async_ keyword.

## Setting Pin Modes

### set_pin_mode_analog_input

```python
 def set_pin_mode_analog_input(self, pin_number, callback=None, differential=0)

    Set a pin as an analog input.

    :param pin_number: arduino pin number

    :param callback: callback function

    :param differential: When comparing the previous value and the current value, if the
                         difference exceeds the differential. This value needs to be equaled 
                         or exceeded for a callback report to be generated.

    callback returns a data list:

    [pin_type, pin_number, pin_value, raw_time_stamp]

    The pin_type for analog input pins = 2
```
**Examples:**

1. telemetrix: [analog_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/analog_input.py)
2. telemtrix-aio: [analog_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/analog_input.py)

**Notes:** 

1. Both telemetrix and telemetrix-aio refer to analog pins using the numeric portion of the pin number only. 
For example, pin A3 is referred to as pin 3.
2. Data reporting via callbacks for this pin begins immediately after this method is called. 

### set_pin_mode_analog_output
This mode is used to place a digital pin into PWM output mode. Arduino refers to this mode of operation as
analog output mode.

```python
```python
 def set_pin_mode_analog_output(self, pin_number)

    Set a pin as an analog input.

    :param pin_number: arduino pin number

    :param callback: callback function


    callback returns a data list:

    [pin_type, pin_number, pin_value, raw_time_stamp]

    The pin_type for analog input pins = 2
```

**Examples:**

1. telemetrix:  [fade.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/fade.py)
2. telemetrix-aio: [fade.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/fade.py)

**Notes:** 

Only specific digital pins support this mode. Check with the Arduino documentation
for your board to determine which pins support PWM.

### set_pin_mode_dht
When this method is called, a check for a valid DHT device is made. A report 
is generated and sent back through the callback, indicating that a DHT device was 
found or an error occurred.

```
 def set_pin_mode_dht(self, pin, callback=None)

    This method sets a pin as a DHT22 pin

    :param pin: dht22 pin

    :param callback: callback function

    Error Callback: [Callback 0=DHT REPORT, DHT_ERROR=0, PIN, Error Number, Time]

    Valid Data Callback: Callback 0=DHT REPORT, DHT_DATA=1, PIN, Humidity, Temperature Time]
```
**Examples:** 

1. telemetrix: [dht.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/dht.py)
2. telemetric-aio: [dht.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/dht.py)

### set_pin_mode_digital_input
```python
 def set_pin_mode_digital_input(self, pin_number, callback=None)

    Set a pin as a digital input.

    :param pin_number: arduino pin number

    :param callback: callback function

    callback returns a data list:

    [pin_type, pin_number, pin_value, raw_time_stamp]

    The pin_type for digital input pins = 0
```

**Examples:** 

1. telemetrix: [digital_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/digital_input.py)
2. telemetrix-aio: [digital_input_debounce.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/digital_input.py)

**Notes:** 

Data reporting via callbacks for this pin begins immediately after this method is called. 


### set_pin_mode_digital_input_pullup

```python
 def set_pin_mode_digital_input_pullup(self, pin_number, callback=None)

    Set a pin as a digital input with pullup enabled.

    :param pin_number: arduino pin number

    :param callback: callback function

    callback returns a data list:

    [pin_type, pin_number, pin_value, raw_time_stamp]

    The pin_type for digital input pins with pullups enabled = 11

```
**Example:** 

1. telemetrix: [digital_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/digital_input_pullup.py)
2. telemetrix-aio: [digital_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/digital_input_pullup.py)
**Notes:** 

Data reporting via callbacks for this pin begins immediately after this method is called. 

### set_pin_mode_digital_output

```python
 def set_pin_mode_digital_output(self, pin_number)

    Set a pin as a digital output pin.

    :param pin_number: arduino pin number

```
**Examples:** 

1. telemetrix: [blink.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/blink.py)
2. telemetrix-aio: [blink.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/blink.py)



### set_pin_mode_i2c
```python
ddef set_pin_mode_i2c(self, i2c_port=0):
    """
    Establish the standard Arduino i2c pins for i2c utilization.

    :param i2c_port: 0 = i2c1, 1 = i2c2
                     Some Arduino-core boards support a secondary i2c port.
                     This parameter selects the port. Both ports may
                     be active.
                     The secondary port needs to be enabled by enabling
                     a #ifdef in the Telemetrix4Arduino sketch.


    NOTES: 1. THIS METHOD MUST BE CALLED BEFORE ANY I2C REQUEST IS MADE
           2. Callbacks are set within the individual i2c read methods of this
          API.

          See i2c_read, or i2c_read_restart_transmission.

    """
```

**Examples:**

1. telemetrix: primary i2c port [i2c_adxl345_accelerometer.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/i2c_adxl345_accelerometer.py)
2. telemetrix: secondary i2c port [i2c_adxl345_accelerometer2.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/i2c_adxl345_accelerometer2.py)
2. telemetrix-aio : primary i2c port [i2c_adxl345_accelerometer.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/i2c_adxl345_accelerometer.py)
2. telemetrix-aio : secondary i2c port [i2c_adxl345_accelerometer2.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/i2c_adxl345_accelerometer2.py)

### set_pin_mode_servo
```python
  def set_pin_mode_servo(self, pin_number, min_pulse=544, max_pulse=2400)

    Attach a pin to a servo motor

    :param pin_number: pin

    :param min_pulse: minimum pulse width

    :param max_pulse: maximum pulse width
```
**Examples:**

1. telemetrix: [servo.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/servo.py)
2. telemetrix-aio: [servo.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/servo.py)


### set_pin_mode_sonar
```python
  def set_pin_mode_sonar(self, trigger_pin, echo_pin, callback=None)

    :param trigger_pin:

    :param echo_pin:

    :param callback: callback

    callback data: [PrivateConstants.SONAR_DISTANCE, trigger_pin, distance_value, time_stamp]

```
**Examples:**

1. telemetrix:  [hc-sr04_distance_sensor.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/hc-sr04_distance_sensor.py)
2. telemetrix-aio:  [hc-sr04_distance_sensor.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/hc-sr04_distance_sensor.py)




<br>
<br>

Copyright (C) 2020 Alan Yorinks. All Rights Reserved.
