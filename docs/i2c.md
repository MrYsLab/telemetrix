# Communicating With I2C Devices
Both telemetrix and telemetrix-aio have the capability to support two i2c buses.
The default is always enabled. To enable the secondary bus, edit the Telemetrix4Arduino.ino
file, and uncomment the following line:

```
// uncomment out the next line to create a 2nd i2c port
//#define SECOND_I2C_PORT

#ifdef SECOND_I2C_PORT
// Change the pins to match SDA and SCL for your board
#define SECOND_I2C_PORT_SDA PB3
#define SECOND_I2C_PORT_SCL PB10
```

Make sure that the pin designations for the secondary port match those for your board.


**NOTE :** Examples for i2c read and write may be found in these examples.

telemetrix primary port:  [i2c_adxl345_accelerometer.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/i2c_adxl345_accelerometer.py)

telemetrix secondary port:  [i2c_adxl345_accelerometer2.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/i2c_adxl345_accelerometer2.py) 

telemetrix-aio primary port:  [i2c_adxl345_accelerometer.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/i2c_adxl345_accelerometer.py)

telemetrix-aio secondary port:  [i2c_adxl345_accelerometer2.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/i2c_adxl345_accelerometer2.py) 
  

## Read Commands

### i2c_read

```python
 def i2c_read(self, address, register, number_of_bytes, callback=None, 
              i2c_port=0, write_register=True)

    Read the specified number of bytes from the specified register for
    the i2c device.

    :param address: i2c device address

    :param register: i2c register (or None if no register selection is needed)

    :param number_of_bytes: number of bytes to be read

    :param callback: Required callback function to report i2c data as
                     a result of read command

    :param i2c_port: 0 = default, 1 = secondary

    :param write_register: If True, the register is written before read 
                           Else, the write is suppressed

    callback returns a data list:

    [I2C_READ_REPORT, address, register, count of data bytes, 
     data bytes, time-stamp]
    
 
```
**Examples:**

See NOTE above.



### i2c_read_restart_transmission

```python
 def i2c_read_restart_transmission(self, address, register, number_of_bytes, 
                                   callback=None, i2c_port=0, write_register=True)

    Read the specified number of bytes from the specified 
    register for the i2c device. This restarts the transmission after the read. 
    It is required for some i2c devices such as the MMA8452Q accelerometer.

    :param address: i2c device address

    :param register: i2c register (or None if no register selection is needed)

    :param number_of_bytes: number of bytes to be read

    :param callback: Required callback function to report i2c data 
                     as a result of read command

    :param i2c_port: 0 = default 1 = secondary

    :param write_register: If True, the register is written before read
                        Else, the write is suppressed

    callback returns a data list:

    [I2C_READ_REPORT, address, register, count of data bytes, 
     data bytes, time-stamp]
```

**Examples:**

See NOTE above.


## Write Command

### i2c_write
```python
 def i2c_write(self, address, args, i2c_port=0)

    Write data to an i2c device.

    :param address: i2c device address

    :param i2c_port: 0= port 1, 1 = port 2

    :param args: A variable number of bytes to be sent to the device passed in as a list
```

**Examples:**

See NOTE above.
<br>
<br>

Copyright (C) 2020-21 Alan Yorinks. All Rights Reserved.
