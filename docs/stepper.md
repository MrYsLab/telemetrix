
### stepper_get_current_position

```python
def stepper_get_current_position(self, motor_id, current_position_callback)

    Request the current motor position from the server.

    :param motor_id: 0 - 7

    :param current_position_callback: required callback function to receive report

    :return: The current motor position returned via the callback as a list:

    [REPORT_TYPE=17, motor_id, current position in steps, time_stamp]

    Positive is clockwise from the 0 position.
```

**Examples:** 

1. telemetrix: [stepper_set_and_get.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_set_and_get.py)

### stepper_get_distance_to_go

```python
def stepper_get_distance_to_go(self, motor_id, distance_to_go_callback)

    Request the distance from the current position to the target 
    position from the server.

    :param motor_id: 0 - 7

    :param distance_to_go_callback: required callback function 
                                    to receive report

    :return: The distance to go is returned via the callback as a list:

    [REPORT_TYPE=15, motor_id, distance in steps, time_stamp]

    A positive distance is clockwise from the current position.
```

**Examples:** 

1. telemetrix: [stepper_set_and_get.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_set_and_get.py)

### stepper_get_target_position

```python
def stepper_get_target_position(self, motor_id, target_callback)

    Request the most recently set target position from the server.

    :param motor_id: 0 - 7

    :param target_callback: required callback function to receive report

    :return: The distance to go is returned via the callback as a list:

    [REPORT_TYPE=16, motor_id, target position in steps, time_stamp]

    Positive is clockwise from the 0 position.
```

**Examples:** 

1. telemetrix: [stepper_set_and_get.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_set_and_get.py)

### stepper_is_running

```python
def stepper_is_running(self, motor_id, callback)

    Checks to see if the motor is currently running to a target.

    Callback returns True if the speed is not zero or not at the target position.

    :param motor_id: 0-4

    :param callback: required callback function to receive report

    :return: The current running state returned via the callback as a list:

    [REPORT_TYPE=18, motor_id, True or False for running state, time_stamp]
```

**Examples:** 

1. telemetrix: [stepper_absolute.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_absolute.py)
2. telemetrix-aio : [stepper_absolute.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/stepper_absolute.py)

### stepper_move

```python
def stepper_move(self, motor_id, relative_position)

    Set the target position relative to the current position.

    :param motor_id: motor id: 0 - 7

    :param relative_position: The desired position relative to the 
                              current position.
                              Negative is anticlockwise from the 
                              current position. 
                              Maximum value is 32 bits.
```

**Examples:** 

1. telemetrix: [stepper_relative.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_relative.py)
2. telemetrix-aio : [stepper_relative.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/stepper_relative.py)

### stepper_move_to

```python
def stepper_move_to(self, motor_id, position)

    Set an absolution target position. If position is positive, the movement is 
    clockwise, else it is counter-clockwise.

    The run() function (below) will try to move the motor 
    (at most one step per call) from the current position to the target
    position set by the most recent call to this function. 
    Caution: moveTo() also recalculates the speed for the next step. 
    If you are trying to use constant speed movements, you should 
    call setSpeed() after calling moveTo().

    :param motor_id: motor id: 0 - 7

    :param position: target position. Maximum value is 32 bits.
```

**Examples:** 


1. telemetrix: [stepper_run_speed_to_position.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_run_speed_to_position.py)

### stepper_run

```python
def stepper_run(self, motor_id, completion_callback=None)

    This method steps the selected motor based on the current speed.

    Once called, the server will continuously attempt to step the motor.

    :param motor_id: 0 - 7

    :param completion_callback: call back function to receive
                                motion complete notification

    callback returns a data list:

    [report_type, motor_id, raw_time_stamp]

    The report_type = 19
```
**Examples:** 

1. telemetrix: [stepper_absolute.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_absolute.py)
2. telemetrix-aio : [stepper_absolute.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/stepper_absolute.py)

### stepper_run_speed

```python
def stepper_run_speed(self, motor_id)

    This method steps the selected motor based at a constant speed as 
    set by the most recent call to stepper_set_max_speed(). 
    The motor will run continuously.

    Once called, the server will continuously attempt to step the motor.

    :param motor_id: 0 - 7
```

**Examples:** 

1. telemetrix: [stepper_continuous.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_continuous.py)
2. telemetrix-aio : [stepper_continuous.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/stepper_continuous.py)

### stepper_run_speed_to_position

```python

def stepper_run_speed_to_position(self, motor_id, completion_callback=None)

    Runs the motor at the currently selected speed until the target
    position is reached.

    Does not implement accelerations.

    :param motor_id: 0 - 7

    :param completion_callback: call back function to receive motion 
                                complete notification

    callback returns a data list:

    [report_type, motor_id, raw_time_stamp]

    The report_type = 19
```

**Examples:** 

1. telemetrix: [stepper_run_speed_to_position.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_run_speed_to_position.py)


### stepper_set_acceleration

```python
def stepper_set_acceleration(self, motor_id, acceleration)

    Sets the acceleration/deceleration rate.

    :param motor_id: 0 - 7

    :param acceleration: The desired acceleration in steps per 
                         second per second. 
                         Must be > 0.0. This is an expensive call since it 
                         requires a square root to be calculated on the server. 
                         Dont call more often than needed.
```
**Examples:** 

1. telemetrix: [stepper_absolute.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_absolute.py)
2. telemetrix-aio : [stepper_absolute.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/stepper_absolute.py)

### stepper_set_current_position
```python
def stepper_set_current_position(self, motor_id, position)

    Resets the current position of the motor, so that wherever the motor happens 
    to be right now is considered to be the new 0 position. 
    Useful for setting a zero position on a stepper after an 
    initial hardware positioning move.

    Has the side effect of setting the current motor speed to 0.

    :param motor_id: 0 - 7

    :param position: Position in steps. This is a 32 bit value
```

**Examples:** 

1. telemetrix: [stepper_set_and_get.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_set_and_get.py)

### stepper_set_max_speed

```python
def stepper_set_max_speed(self, motor_id, max_speed)

    Sets the maximum permitted speed. The stepper_run() function will 
    accelerate up to the speed set by this function.

    Caution: the maximum speed achievable depends on your processor 
    and clock speed. The default maxSpeed is 1 step per second.

    Caution: Speeds that exceed the maximum speed supported by the 
    processor may result in non-linear accelerations and decelerations.

    :param motor_id: 0 - 7

    :param max_speed: 1 - 1000
```

**Examples:** 

1. telemetrix: [stepper_absolute.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_absolute.py)
2. telemetrix-aio : [stepper_absolute.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/stepper_absolute.py)

### stepper_set_speed

```python
def stepper_set_speed(self, motor_id, speed)

    Sets the desired constant speed for use with stepper_run_speed().

    :param motor_id: 0 - 7

    :param speed: 0 - 1000 The desired constant speed in steps 
                  per second. 
                  Positive is clockwise. Speeds of more than 1000 steps 
                  per second are unreliable. Speed accuracy depends on 
                  the Arduino crystal. 
                  Jitter depends on how frequently you call the 
                  stepper_run_speed() method. The speed will be 
                  limited by the current value of stepper_set_max_speed().
```

**Examples:** 


1. telemetrix: [stepper_run_speed_to_position.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_run_speed_to_position.py)

### Additional Methods

**The following methods are included for AccelStepper compatibility. 
No examples are provided for these methods.**

### stepper_disable_outputs

```python
def stepper_disable_outputs(self, motor_id)

    Disable motor pin outputs by setting them all LOW.

    Depending on the design of your electronics this may turn off the power 
    to the motor coils, saving power.

    This is useful to support Arduino low power modes: 
    disable the outputs during sleep and then re-enable with enableOutputs() 
    before stepping again.

    If the enable Pin is defined, sets it to OUTPUT mode and clears 
    the pin to disabled.

    :param motor_id: 0 - 7
```

### stepper_enable_outputs

```python
def stepper_enable_outputs(self, motor_id)

    Enable motor pin outputs by setting the motor pins to OUTPUT mode.

    If the enable Pin is defined, sets it to OUTPUT mode and sets 
    the pin to enabled.

    :param motor_id: 0 - 7
```

### stepper_get_max_speed

```python
def stepper_get_max_speed(self, motor_id)

    Returns the maximum speed configured for this stepper that was 
    previously set by stepper_set_max_speed()

    Value is stored in the client, so no callback is required.

    :param motor_id: 0 - 7

    :return: The currently configured maximum speed.
```

### stepper_get_speed

```python
def stepper_get_speed(self, motor_id)

    Returns the most recently set speed. that was previously set 
    by stepper_set_speed();

    Value is stored in the client, so no callback is required.

    :param motor_id: 0 - 7
```

### stepper_set_3_pins_inverted

```python
def stepper_set_3_pins_inverted(self, motor_id, direction=False, 
                                step=False, enable=False)

    Sets the inversion for stepper driver pins.

    :param motor_id: 0 - 7

    :param direction: True=inverted or False

    :param step: True=inverted or False

    :param enable: True=inverted or False
```

### stepper_set_4_pins_inverted

```python
def stepper_set_4_pins_inverted(self, motor_id, pin1_invert=False, 
                                pin2_invert=False, pin3_invert=False, 
                                pin4_invert=False, enable=False)

    Sets the inversion for 2, 3 and 4 wire stepper pins

    :param motor_id: 0 - 7

    :param pin1_invert: True=inverted or False

    :param pin2_invert: True=inverted or False

    :param pin3_invert: True=inverted or False

    :param pin4_invert: True=inverted or False

    :param enable: True=inverted or False
```

### stepper_set_enable_pin

```python
def stepper_set_enable_pin(self, motor_id, pin=255)

    Sets the enable pin number for stepper drivers. 
    0xFF indicates unused (default).

    Otherwise, if a pin is set, the pin will be turned on when 
        
    enableOutputs() is called and switched off when disableOutputs() is called.

    :param motor_id: 0 - 7 
    
    :param pin: 0-0xff
```

### stepper_set_min_pulse_width

```python
def stepper_set_min_pulse_width(self, motor_id, minimum_width)

    Sets the minimum pulse width allowed by the stepper driver.

    The minimum practical pulse width is approximately 20 microseconds.

    Times less than 20 microseconds will usually result in 20 microseconds or so.

    :param motor_id: 0 -7

    :param minimum_width: A 16 bit unsigned value expressed in microseconds.
```

### stepper_stop

```python
def stepper_stop(self, motor_id)

    Sets a new target position that causes the stepper to stop as quickly as 
    possible, using the current speed and acceleration parameters.

    :param motor_id: 0 - 7
```

