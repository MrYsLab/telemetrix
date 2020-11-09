# A Use Case - The DHT 22 Sensor

The Telemetrix Project comes pre-packaged with support for a fixed set of sensors and actuators.
But, what if you want to add support for something outside of the base set?

In this section, you will learn how to add custom support for a sensor or actuator of your choosing.

We will be using the DHT 22 temperature/humidity sensor to 
illustrate how to extend the Telemetrix Project's capabilities for discussion purposes.
 
## The Command And Reporter Packets

The Telemetrix clients and server communicate by exchanging data packets over the serial link. 

The data packets originating from the client are called _command_ packets. 

The data packets originating from the server are called _reporter_ packets.

The format for both command and reporter packets is the same.

<img src="../images/packet.png">


The _packet length_ and _packet ID_ portions of the packet are each one byte in length. 
The total payload length is of variable size.

The packet length byte represents the total length in bytes of the payload section of the packet.
Note that the length does not include the packet length byte.

When Telemetrix4Arduino receives a command in the get_next_command function, 
all of the bytes that follow the payload ID are placed into a command_buffer for processing.

When a Telemetrix client receives a report, the _reporter method also places all of the bytes following the payload
ID into the response_data buffer for processing.
 
## Coping With Various Data Types With A Byte-Oriented Serial Link
When data is sent across the serial link, it is sent as a series of bytes.
Some data types, such as integers and floating-point values, are larger than a single byte.
For the Telemetrix Project, an integer value is two bytes in length, and a floating-point value is four bytes
in length.

When sending a value larger than a byte in length, the multi-byte values are disassembled into 
individual bytes before transmission.
When received, the individual bytes are reassembled into the original multi-byte value. 
 For all data items that must be represented in this manner, by convention, the most significant byte 
 is the first byte transmitted, followed by all subsequent bytes in descending byte order.

For example, the DHT 22 sensor expresses temperature and humidity values as floating-point. To send a report containing
these values to the client, they must first be converted to individual bytes.

Using humidity as an example, let's see how this is done:

```
// get humidity
dht_data = dhts[i].dht_sensor->getHumidity();
memcpy(&report_message[4], &dht_data, sizeof dht_data);
```
The humidity is retrieved by calling the DHTNEW method,  _getHumdity_.
The floating-point value returned in dht_data is converted to bytes, by using
the memcpy function. In the example above, the bytes are copied into a report_message
buffer in MSB order.

On the client side, the converted bytes need to be reassembled into floats before providing
the data values to the user application.

```python
f_humidity = bytearray(data[2:6])
f_temperature = bytearray(data[6:])
message = [PrivateConstants.DHT_REPORT, data[0], data[1],
           (struct.unpack('<f', f_humidity))[0],
           (struct.unpack('<f', f_temperature))[0],
           time.time()]
```

In the example above, the humidity and temperature values are first extracted from the incoming report
as bytearrays. Then using the Python struct library, the bytearrays are reassembled into their
 original floating-point values.


## Preparing For The New Extension

Before jumping directly into coding, there are a few things you should consider when designing
your extension.

1. Review the library's API to select the methods you wish to support.

    You may support the full set of library functions or a subset. For this example,
    only the minimum functions will be supported to help keep things as simple as possible.
    
    The library chosen for the DHT is the [dhtnew library](https://github.com/RobTillaart/DHTNew).

2. Determine if there is a time constraint on how often a device can be accessed.

      The DHT 22, for example, can only be read every 2 seconds to receive valid data. 
      We will demonstrate how to support this restriction in a non-blocking manner.**

3. Determine the number of instances of the device you wish to support.

     For the DHT 22, up to six devices are supported.
    
## Implementing The New Extension

Below are the steps used for adding the DHT extension. We will use the telemetrix client for illustration
purposes. Modifying telemetrix-aio would take a similar approach. 

Each step will be discussed in detail in the following sections.
The assumption is that the new extension will ultimately result in continuous report generation
 without any additional API calls. 
Your device may have different requirements, and you will need to adjust things for your particular case.

1. Add a new **client** command to be transmitted to the server.

2. Add a new command handler on the **server** to process the command.

3. Add a new function to the **server** to continuously monitor the device and generate data reports.

4. Add a new function to the **client** to handle the new incoming reports.

### Adding A New Client Command
<p><b>1. Define A New Command Value</b></p>

To add a new command to the API, define a new command value in
[private_constants.py](https://github.com/MrYsLab/telemetrix/blob/master/telemetrix/private_constants.py).
```python
class PrivateConstants:
    """
    This class contains a set of constants for telemetrix internal use .
    """

    # commands
    # send a loop back request - for debugging communications
    LOOP_COMMAND = 0
    SET_PIN_MODE = 1  # set a pin to INPUT/OUTPUT/PWM/etc
    DIGITAL_WRITE = 2  # set a single digital pin value instead of entire port
    ANALOG_WRITE = 3
    MODIFY_REPORTING = 4
    GET_FIRMWARE_VERSION = 5
    ARE_U_THERE = 6  # Arduino ID query for auto-detect of telemetrix connected boards
    SERVO_ATTACH = 7
    SERVO_WRITE = 8
    SERVO_DETACH = 9
    I2C_BEGIN = 10
    I2C_READ = 11
    I2C_WRITE = 12
    SONAR_NEW = 13
    DHT_NEW = 14 #<-----------New Command For the DHT!!!!!!!!!!!!!
    STOP_ALL_REPORTS = 15
    SET_ANALOG_SCANNING_INTERVAL = 16
```
Here the command DHT_NEW was added.

<p><b>2. Define the maximum number of DHT devices to be supported.</b></p>

Add this value to private_contants.py
```python
# Maximum number of dht devices allowed
 MAX_DHTS = 6
```

<p><b>3. Add storage to telemetrix.py to keeps track of the number of currently active DHT devices and
their associated callback functions.</b></p>

```python
self.dht_callbacks = {}

self.dht_count = 0
```
The dht_callbacks dictionary uses the pin number for the DHT device as a key to retrieve its associated callback 
function.

The dht_count variable keeps track of the currently active DHT devices.

<p><b>4. Add a command method to telemetrix.py to command the server to add a new DHT device.</b></p>

```
def set_pin_mode_dht(self, pin, callback=None):
        """
        :param pin: connection pin
        :param callback: callback function
        Error Callback: [Callback 0=DHT REPORT, DHT_ERROR=0, PIN, Error Number, Time]
        Valid Data Callback: Callback 0=DHT REPORT, DHT_DATA=1, PIN, Humidity, Temperature Time]
        """

        if not callback:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError('set_pin_mode_dht: A Callback must be specified')

        if self.dht_count < PrivateConstants.MAX_DHTS - 1:
            self.dht_callbacks[pin] = callback
            self.dht_count += 1

            command = [PrivateConstants.DHT_NEW, pin]
            self._send_command(command)
        else:
            if self.shutdown_on_exception:
                self.shutdown()
            raise RuntimeError(f'Maximum Number Of DHTs Exceeded - set_pin_mode_dht fails for pin {pin}')
```
The name set_pin_mode_dht, was chosen to stay consistent with the telemetrix naming conventions.
Because DHT devices generate reports, we ensure that the user specifies a callback function for the device.
The callback is added to dht_callbacks, and the number of active DHT devices is incremented. If the maximum number of DHT 
devices is exceeded, a RuntimeError is raised.  Otherwise, a command data packet is built and sent to the server.

**NOTE:** The _send_command method will automatically calculate the packet length and append it to the packet.



### Adding A New Server Command Handler
<p><b>1. Add the library to the list of #includes</b></p>

```
#include <Arduino.h>
#include "Telemetrix4Arduino.h"
#include <Servo.h>
#include <Ultrasonic.h>
#include <Wire.h>
#include <dhtnew.h> // Adding dhtnew
```

<p><b>2. Create A Name For The New Command Handler Function And Declare It As Extern</b></p>
```
// Create forward references for all the command handlers.
// If you add a new command, you must add the command handler
// here as well.

extern void serial_loopback();

extern void set_pin_mode();

extern void digital_write();

extern void analog_write();

extern void modify_reporting();

extern void get_firmware_version();

extern void are_you_there();

extern void servo_attach();

extern void servo_write();

extern void servo_detach();

extern void i2c_begin();

extern void i2c_read();

extern void i2c_write();

extern void sonar_new();

extern void dht_new(); // The New Command Handler

extern void stop_all_reports();

extern void set_analog_scanning_interval();
```
<p><b>3. Define A Value For The Command That Matches The Value Defined In The Client</b></p>

```
// Commands -received by this sketch
// Add commands retaining the sequential numbering.
// The order of commands here must be maintained in the command_table.
#define SERIAL_LOOP_BACK 0
#define SET_PIN_MODE 1
#define DIGITAL_WRITE 2
#define ANALOG_WRITE 3
#define MODIFY_REPORTING 4 // mode(all, analog, or digital), pin, enable or disable
#define GET_FIRMWARE_VERSION 5
#define ARE_U_THERE 6
#define SERVO_ATTACH 7
#define SERVO_WRITE 8
#define SERVO_DETACH 9
#define I2C_BEGIN 10
#define I2C_READ 11
#define I2C_WRITE 12
#define SONAR_NEW 13
#define DHT_NEW 14 // The Command value
#define STOP_ALL_REPORTS 15
#define SET_ANALOG_SCANNING_INTERVAL 16

```

<p><b>4. Update The Command Table With The New Command</b></p>

The data structures are provided below. To update the table, increase
the size of the command_table to accept the new command.

The command_table contains pointers to the command functions. Note
that you may optionally specify the command without the & operator. The
compiler interprets the entry the same way in both cases.

The command value defined above, the value 14 for DHTNEW, acts as an index 
into the command_table when fetching the function pointer. Make sure
to order the command_table appropriately.

```
// When adding a new command update the command_table.
// The command length is the number of bytes that follow
// the command byte itself, and does not include the command
// byte in its length.
// The command_func is a pointer the command's function.
struct command_descriptor
{
    // a pointer to the command processing function
    void (*command_func)(void);
};

// An array of pointers to the command functions

// If you add new commands, make sure to extend the siz of this
// array.
command_descriptor command_table[17] =
    {
        {&serial_loopback},
        {&set_pin_mode},
        {&digital_write},
        {&analog_write},
        {&modify_reporting},
        {&get_firmware_version},
        {&are_you_there},
        {&servo_attach},
        {&servo_write},
        {&servo_detach},
        {&i2c_begin},
        {&i2c_read},
        {&i2c_write},
        {&sonar_new},
        {dht_new}, // The new function
        {stop_all_reports},
        {set_analog_scanning_interval}
    };
```
<p><b>5. Create An Array Of DHT Descriptor Structures To Support The Feature</b></p>

```

#define MAX_DHTS 6                // max number of devices

// DHT Descriptor
struct DHT
{
    uint8_t pin;
    unsigned int last_value;     // this value is reserved for future use
                                 // if a report should be generated
    DHTNEW *dht_sensor;
};

// an array of dht descriptor objects
DHT dhts[MAX_DHTS];

byte dht_index = 0; // index into the dhts array
```

<p><b>6. Create The Command Handler Function</b></p>

```
/***********************************
 * DHT adding a new device
 **********************************/

void dht_new()
{
    int d_read;
    // report consists of:
    // 0 - byte count
    // 1 - report type
    // 2 - dht report subtype
    // 3 - pin number
    // 4 - error value

    // pre-build an error report in case of a read error
    byte report_message[5] = {4, (byte)DHT_REPORT, (byte)DHT_READ_ERROR, (byte)0, (byte)0};

    dhts[dht_index].dht_sensor = new DHTNEW((uint8_t)command_buffer[0]);
    dhts[dht_index].dht_sensor->setType();

    dhts[dht_index].pin = command_buffer[0];
    d_read = dhts[dht_index].dht_sensor->read();

    // if read return == zero it means no errors.
    if (d_read == 0)
    {
        dht_index++;
    }
    else
    {
        // error found
        // send report and release the dht object

        report_message[3] = command_buffer[0]; // pin number
        report_message[4] = d_read;
        Serial.write(report_message, 5);
        delete (dhts[dht_index].dht_sensor);
    }
}
```
When a DHT is added, a read is performed to see if there are any issues with the device.
If the read returns a zero, then there are no issues and nothing to report. However, a non-zero
value is an error indicator. The error value is returned as a report.

### Add A New Server Function To Continuously Monitor The Device

<p><b>1. Create A Device Scanner Function For Active DHT Devices</b></p>
We are going to create the _scan_dhts_ scanning function and then call the function in 
the loop section of the sketch.

The scan_dhts function prebuilds a report_message buffer assuming that the read
will return valid data.  The format for the report is shown in the comments for the function.
For valid data, the floating-point values are copied to the buffer as bytes, and a report is sent across the link.

If an error is returned as a result of the read, byte 2 of the report, the report sub-type is changed 
from DHT_DATA to DHT_ERROR, and the packet length is changed to a value of 4 bytes. The report is then 
sent across the serial link.


```
void scan_dhts()
{
    // prebuild report for valid data
    // reuse the report if a read command fails

    // data returned is in floating point form - 4 bytes
    // each for humidity and temperature

    // byte 0 = packet length
    // byte 1 = report type
    // byte 2 = report sub type - DHT_DATA or DHT_ERROR
    // btye 3 = pin number
    // byte 4 = humidity high order byte for data or error value
    // byte 5 = humidity byte 2
    // byte 6 = humidity byte 3
    // byte 7 = humidity byte 4
    // byte 8 = temperature high order byte for data or
    // byte 9 = temperature byte 2
    // byte 10 = temperature byte 3
    // byte 11 = temperature byte 4
    byte report_message[12] = {11, DHT_REPORT, DHT_DATA, 0, 0, 0, 0, 0, 0, 0, 0, 0};

    byte d_read;

    float dht_data;

    // are there any dhts to read?
    if (dht_index)
    {
        // is it time to do the read? This should occur every 2 seconds
        dht_current_millis = millis();
        if (dht_current_millis - dht_previous_millis > dht_scan_interval)
        {
            // update for the next scan
            dht_previous_millis += dht_scan_interval;

            // read and report all the dht sensors
            for (int i = 0; i < dht_index; i++)
            {
                report_message[3] = dhts[i].pin;
                // get humidity
                dht_data = dhts[i].dht_sensor->getHumidity();
                memcpy(&report_message[4], &dht_data, sizeof dht_data);

                // get temperature
                dht_data = dhts[i].dht_sensor->getTemperature();
                memcpy(&report_message[8], &dht_data, sizeof dht_data);

                Serial.write(report_message, 12);

                // now read do a read for this device for next go around
                d_read = dhts[i].dht_sensor->read();

                if (d_read)
                {
                    // error found
                    // send report
                    //send_debug_info(1, 1);
                    report_message[0] = 4;
                    report_message[1] = DHT_REPORT;
                    report_message[2] = DHT_READ_ERROR;
                    report_message[3] = dhts[i].pin; // pin number
                    report_message[4] = d_read;
                    Serial.write(report_message, 5);
                }
            }
        }
    }
}

```
<p><b>2. Scan The Active DHT Sensors In The Sketch Loop Function</b></p>


```
void loop()
{
    // keep processing incoming commands
    get_next_command();

    if(! stop_reports){ // stop reporting
        scan_digital_inputs();
        scan_analog_inputs();
        scan_sonars();
        scan_dhts(); scan the active DHT sensors.
    }
}
```

### Add a New Client Report Handler

<p><b>1. Add An Entry For The DHT Report To The Report Dispatch Dictionary</b></p>
The report_dispatch dictionary uses report ID values as a key to look up the
handler for the incoming report. The dictionary update method is used when adding a new entry into 
the dispatch dictionary.

```
# The report_dispatch dictionary is used to process
        # incoming report messages by looking up the report message
        # and executing its associated processing method.

        self.report_dispatch = {}

        # To add a command to the command dispatch table, append here.
        self.report_dispatch.update({PrivateConstants.LOOP_COMMAND: self._report_loop_data})
        self.report_dispatch.update({PrivateConstants.DEBUG_PRINT: self._report_debug_data})
        self.report_dispatch.update({PrivateConstants.DIGITAL_REPORT: self._digital_message})
        self.report_dispatch.update({PrivateConstants.ANALOG_REPORT: self._analog_message})
        self.report_dispatch.update({PrivateConstants.FIRMWARE_REPORT: self._firmware_message})
        self.report_dispatch.update({PrivateConstants.I_AM_HERE_REPORT: self._i_am_here})
        self.report_dispatch.update({PrivateConstants.SERVO_UNAVAILABLE: self._servo_unavailable})
        self.report_dispatch.update({PrivateConstants.I2C_READ_REPORT: self._i2c_read_report})
        self.report_dispatch.update({PrivateConstants.I2C_TOO_FEW_BYTES_RCVD: self._i2c_too_few})
        self.report_dispatch.update({PrivateConstants.I2C_TOO_MANY_BYTES_RCVD: self._i2c_too_many})
        self.report_dispatch.update({PrivateConstants.SONAR_DISTANCE: self._sonar_distance_report})
        self.report_dispatch.update({PrivateConstants.DHT_REPORT: self._dht_report})
```
<p><b>2. Create The Report Handler</b></p>

This function builds a report, and looks up the callback function for the DHT device
using the reported pin number as the key and calls the callback function.

```
def _dht_report(self, data):
        """
        This is the dht report handler method.
        :param data:            data[0] = report sub type - DHT_DATA or DHT_ERROR
                                data[1] = pin number
                                data[2] = humidity high order byte or error value if DHT_ERROR
                                data[3] = humidity byte 2
                                data[4] = humidity byte 3
                                data[5] = humidity byte 4
                                data[6] = temperature high order byte for data
                                data[7] = temperature byte 2
                                data[8] = temperature byte 3
                                data[9] = temperature byte 4
        """

        if data[0]:  # DHT_ERROR
            # error report
            # data[0] = report sub type, data[1] = pin, data[2] = error message
            if self.dht_callbacks[data[1]]:
                # Callback 0=DHT REPORT, DHT_ERROR=0, PIN, Error Number, Time
                message = [PrivateConstants.DHT_REPORT, data[0], data[1], data[2], time.time()]
                self.dht_callbacks[data[1]](message)
        else:
            # got valid data DHT_DATA
            f_humidity = bytearray(data[2:6])
            f_temperature = bytearray(data[6:])
            message = [PrivateConstants.DHT_REPORT, data[0], data[1],
                       (struct.unpack('<f', f_humidity))[0],
                       (struct.unpack('<f', f_temperature))[0],
                       time.time()]

            self.dht_callbacks[data[1]](message)
```


