Telemetrix supports the OneWire communications protocol.

**NOTE:** Examples for the OneWire commands and reports may be found here:

For telemetrix: [onewire_ds18x20.py](https://github.com/MrYsLab/telemetrix/blob/master/examples/onewire_ds18x20.py)

For telemetrix-aio: [onewire_ds18x20.py](https://github.com/MrYsLab/telemetrix-aio/blob/master/examples/onewire_ds18x20.py)


## Read Commands

### onewire_read

```python
def onewire_read(self, callback=None):
    """
    Read a byte from the onewire device
    :param callback: required  function to report onewire data as a
               result of read command


    callback returns a data list:
    [ONEWIRE_REPORT, ONEWIRE_READ=29, data byte, time-stamp]

    ONEWIRE_REPORT = 14
    """
```

## Write Commands

### onewire_write
```python
def onewire_write(self, data, power=0):
    """
    Write a byte to the onewire device. If 'power' is one
    then the wire is held high at the end for
    parasitically powered devices. You
    are responsible for eventually de-powering it by calling
    another read or write.

    :param data: byte to write.
    :param power: power control (see above)
    """
```

## Control And Operational Commands

### onewire_crc8

```python
def onewire_crc8(self, address_list, callback=None):
    """
    Compute a CRC check on an array of data.
    :param address_list:

    :param callback: required  function to report a onewire device address

    callback returns a data list:
    [ONEWIRE_REPORT, ONEWIRE_CRC8=32, CRC, time-stamp]

    ONEWIRE_REPORT = 14

    """
```

### onewire_reset

```python
def onewire_reset(self, callback=None):
    """
    Reset the onewire device

    :param callback: required  function to report reset result

    callback returns a list:
    [ReportType = 14, Report Subtype = 25, reset result byte,
                    timestamp]
    """
```

### onewire_reset_search
```python
def onewire_reset_search(self):
    """
    Begin a new search. The next use of search will begin at the first device
    """
```

### onewire_search
```python
def onewire_search(self, callback=None):
    """
    Search for the next device. The device address will returned in the callback.
    If a device is found, the 8 byte address is contained in the callback.
    If no more devices are found, the address returned contains all elements set
    to 0xff.

    :param callback: required  function to report a onewire device address

    callback returns a data list:
    [ONEWIRE_REPORT, ONEWIRE_SEARCH=31, 8 byte address, time-stamp]

    ONEWIRE_REPORT = 14
    """
```

### onewire_select
```python
def onewire_select(self, device_address):
    """
    Select a device based on its address
    :param device_address: A bytearray of 8 bytes
    """
```

### onewire_skip
```python
def onewire_skip(self):
    """
    Skip the device selection. This only works if you have a
    single device, but you can avoid searching and use this to
    immediately access your device.
    """
```
