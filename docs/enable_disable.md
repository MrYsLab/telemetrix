# Analog, Digital, And SONAR Input Pin  Reporting

Callback reporting begins immediately upon setting a pin as either a digital or analog
input pin. If your application should unexpectedly exit without an orderly shutdown,
the Arduino may continue to stream data even though your application has exited.

In this scenario, if you do not re-power the Arduino before restarting your application,
the continuing data stream may cause pymata4 to fail because the data stream is out
of sync with pymata4's state.

One way to avoid this scenario is to turn off reporting before exiting your application.

## disable_all_reporting
This command only affects digital and analog inputs and not SONAR.

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

## sonar_disable
This command stops the server from polling SONAR data for all SONAR devices. 
It is useful when using a SONAR device with a stepper motor. 
The AccelStepper library and Ultrasound libraries interfere with each other. 
To use this feature with a stepper motor, call sonar_disable, move the motor, 
and then call sonar_enable to enable checking the distance. 
Then disable it again and move the motor.


```angular2html
 def sonar_disable(self)

    Disable sonar scanning for all sonar sensors

```
**Examples:** 

1. telemetrix: [sonar_disable.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/sonar_disable.py)
2. telemetrix-aio: [sonar_disable.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/sonar_disable.py)

## sonar_enable
This command reenables sonar reporting after disabling.
```angular2html
 def sonar_enable(self)

    Enable sonar scanning for all sonar sensors
```


**Examples:** 

1. telemetrix: [sonar_disable.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/sonar_disable.py)
2. telemetrix-aio: [sonar_disable.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/sonar_disable.py)

