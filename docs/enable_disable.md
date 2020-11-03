# Analog and Digital Input Pin  Reporting

Callback reporting begins immediately upon setting a pin as either a digital or analog
input pin. If your application should unexpectedly exit without an orderly shutdown,
the Arduino may continue to stream data, even though your application has exited.

In this scenario, if you do not re-power the Arduino before restarting your application,
the continuing data stream may cause pymata4 to fail because the data stream is out
of sync with pymata4's state.

One way of making sure that you do not encounter this scenario is to turn off
reporting before exiting your application.

## disable_all_reporting

```python
 def disable_all_reporting(self)

    Disable reporting for all digital and analog input pins

```

**Examples:** 

1. telemetrix: [digital_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/digital_input.py)
2. telemetrix-aio: [digital_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/digital_input.py)

**Notes:** The code to run this command is commented out. Uncomment if you wish to try it. 

## disable_analog_reporting

```python
  def disable_analog_reporting(self, pin)

    Disables analog reporting for a single analog input.

    :param pin: Pin number.
```

**Examples:** 

1. telemetrix: [analog_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/analog_input.py)
2. telemetrix-aio: [analog_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/analog_input.py)

**Notes:** The code to run this command is commented out. Uncomment if you wish to try it. 

## disable_digital_reporting
```python
 def disable_digital_reporting(self, pin)

    Disables digital reporting for a single digital input.

    :param pin: Pin number.
```
**Examples:** 

1. telemetrix: [digital_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/digital_input.py)
2. telemetrix-aio: [digital_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/digital_input.py)

**Notes:** The code to run this command is commented out. Uncomment if you wish to try it. 

## enable_analog_reporting
```python
   def enable_analog_reporting(self, pin)

    Enables analog reporting for the specified pin.

    :param pin: Analog pin number. For example for A0, the number is 0.
```

1. telemetrix: [analog_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/analog_input.py)
2. telemetrix-aio: [analog_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/analog_input.py)

## enable_digital_reporting
```python
  def enable_digital_reporting(self, pin)

    Enable reporting on the specified digital pin.

    :param pin: Pin number.
```

**Examples:** 

1. telemetrix: [digital_input.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/digital_input.py)
2. telemetrix-aio: [digital_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/digital_input.py)

**Notes:** The code to run this command is commented out. Uncomment if you wish to try it. 
<br>
<br>

Copyright (C) 2020 Alan Yorinks. All Rights Reserved.
