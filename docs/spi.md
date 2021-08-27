The SPI communication protocol is supported on the standard SPI pin set specified for 
your MCU.

**NOTE:** Examples for SPI read and write may be found here:

For telemetrix: [spi_mpu9250.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/spi_mpu9250.py)

For telemetrix-aio: [spi_mpu9250.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/spi_mpu9250.py)

## Read Commands

### spi_read_blocking
```python
def spi_read_blocking(self, register_selection, number_of_bytes_to_read,
                      call_back=None):
    """
    Read the specified number of bytes from the specified SPI port and
    call the callback function with the reported data.

    :param register_selection: Register to be selected for read.

    :param number_of_bytes_to_read: Number of bytes to read

    :param call_back: Required callback function to report spi data as a
               result of read command


    callback returns a data list:
    [SPI_READ_REPORT, count of data bytes read, data bytes, time-stamp]

    SPI_READ_REPORT = 13

    """
```

## Write Commands

### spi_write_blocking
```python
def spi_write_blocking(self, bytes_to_write):
    """
    Write a list of bytes to the SPI device.

    :param bytes_to_write: A list of bytes to write. This must
                            be in the form of a list.

    """
```

## Control And Operational Commands

### spi_cs_control
```python
def spi_cs_control(self, chip_select_pin, select):
    """
    Control an SPI chip select line
    :param chip_select_pin: pin connected to CS

    :param select: 0=select, 1=deselect
    """
```

### spi_set_format
```python
def spi_set_format(self, clock_divisor, bit_order, data_mode):
    """
    Configure how the SPI serializes and de-serializes data on the wire.

    See Arduino SPI reference materials for details.

    :param clock_divisor:

    :param bit_order:

                        LSBFIRST = 0

                        MSBFIRST = 1 (default)

    :param data_mode:

                        SPI_MODE0 = 0x00 (default)

                        SPI_MODE1  = 0x04

                        SPI_MODE2 = 0x08

                        SPI_MODE3 = 0x0C

    """
```
<br>
<br>


Copyright (C) 2021 Alan Yorinks. All Rights Reserved.