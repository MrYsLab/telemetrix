# Setting Pin and Device Values
In this section, we discuss writing data to:

* Digital pins.
* Digital pin PWM output (Analog Write).
* Servo motors.


**Note:** I2C devices are discussed in the [next section](../i2c)
 of this guide. 
 
## analog_write

```python
 def analog_write(self, pin, value)

    Set the specified pin to the specified value.

    :param pin: arduino pin number

    :param value: pin value (0-255)

```

**Examples:** 

1. telemetrix: [fade](https://github.com/MrYsLab/telemetrix/blob/master/examples/fade.py)
2. telemetrix-aio: [fade](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/fade.py)

## digital_write

```python
  def digital_write(self, pin, value)

    Set the specified pin to the specified value.

    :param pin: arduino pin number

    :param value: pin value (1 or 0)

```
**Examples:** 

1. telemetrix: [blink](https://github.com/MrYsLab/telemetrix/blob/master/examples/blink.py)
2. telemetrix-aio: [blink](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/blink.py)


## servo_write

```python
 def servo_write(self, pin_number, angle)

    Set a servo attached to a pin to a given angle.

    :param pin_number: pin

    :param angle: angle (0-180)
```

**Examples:** 

1. telemetrix: [servo](https://github.com/MrYsLab/telemetrix/blob/master/examples/servo.py)
2. telemetrix-aio: [servo](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/servo.py)


**Notes:** 

For an angular servo, the position parameter is set between 0 and 180 (degrees).
For a continuous servo, 0 is full-speed in one direction, 
180 is full speed in the other, and a value near 90 is no movement.


