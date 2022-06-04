# Introduction

Before any GPIO pin may be used, its mode of use must be set.

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
When this method is called, a check for a valid DHT device is made. If an error
 is found an error report is generated.

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
2. telemetrix-aio: [digital_input.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/digital_input.py)

**Notes:** 

Data reporting via callbacks for this pin begins immediately after this method is called. 

The pin_type for this report is set to a value of 2 - DIGITAL_REPORT


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

1. telemetrix: [digital_input_pullup.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/digital_input_pullup.py)
2. telemetrix-aio: [digital_input_pullup.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/digital_input_pullup.py)
**Notes:** 

Data reporting via callbacks for this pin begins immediately after this method is called. 

The pin_type for this report is set to a value of 2 - DIGITAL_REPORT


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
3. telemetrix-aio : primary i2c port [i2c_adxl345_accelerometer.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/i2c_adxl345_accelerometer.py)
4. telemetrix-aio : secondary i2c port [i2c_adxl345_accelerometer2.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/i2c_adxl345_accelerometer2.py)

### set_pin_mode_one_wire
```python
def set_pin_mode_one_wire(self, pin):
    """
    Initialize the one wire serial bus.

    :param pin: Data pin connected to the OneWire device
    """
```
**Examples:**

1. telemetrix: [onewire_ds18x20.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/onewire_ds18x20.py)
2. telemetrix-aio: [onewire_ds18x20.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/onewire_ds18x20.py)

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

#### servo_detach

```python
  def servo_detach(self, pin_number)

    Detach a servo for reuse

    :param pin_number: attached pin
```

**Examples:** 

1. telemetrix: [servo](https://github.com/MrYsLab/telemetrix/blob/master/examples/servo.py)
2. telemetrix-aio: [servo](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/servo.py)



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

### set_pin_mode_spi

```python
def set_pin_mode_spi(self, chip_select_list=None):
    """
    Specify the list of chip select pins.

    Standard Arduino MISO, MOSI and CLK pins are used for the board in use.

    Chip Select is any digital output capable pin.

    :param chip_select_list: this is a list of pins to be used for chip select.
                       The pins will be configured as output, and set to high
                       ready to be used for chip select.
                       NOTE: You must specify the chips select pins here!


    command message: [command, number of cs pins, [cs pins...]]
    """
```

1. telemetrix: [spi_mpu9250.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/spi_mpu9250.py)
2. telemetrix-aio : [spi_mpu9250.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/spi_mpu9250.py)

### set_pin_mode_stepper

```python
 def set_pin_mode_stepper(self, interface=1, pin1=2, pin2=3, pin3=4, 
                          pin4=5, enable=True)

    Stepper motor support is implemented as a proxy for the the AccelStepper 
    library for the Arduino.

    https://github.com/waspinator/AccelStepper

    Instantiate a stepper motor.

    Initialize the interface and pins for a stepper motor.

    :param interface: Motor Interface Type:

        1 = Stepper Driver, 2 driver pins required

        2 = FULL2WIRE  2 wire stepper, 2 motor pins required

        3 = FULL3WIRE 3 wire stepper, such as HDD spindle,
            3 motor pins required

        4 = FULL4WIRE, 4 wire full stepper, 4 motor pins
            required

        6 = HALF3WIRE, 3 wire half stepper, such as HDD spindle,
            3 motor pins required

        8 = HALF4WIRE, 4 wire half stepper, 4 motor pins required

    :param pin1: Arduino digital pin number for motor pin 1

    :param pin2: Arduino digital pin number for motor pin 2

    :param pin3: Arduino digital pin number for motor pin 3

    :param pin4: Arduino digital pin number for motor pin 4

    :param enable: If this is True, enable the output pins.

    :return: Motor Reference number
 
```

1. telemetrix: [stepper_absolute.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/stepper_absolute.py)
2. telemetrix-aio : [stepper_absolute.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/stepper_absolute.py)





<br>
<br>

Copyright (C) 2020-21 Alan Yorinks. All Rights Reserved.
