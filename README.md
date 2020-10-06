# The Telemetrix Project

Telemetry is the collection of measurements or other data at remote points and their 
automatic transmission to receiving equipment (telecommunication) for monitoring.

The Telemetrix Project is a telemetry package for Arduino core devices with a serial interface.

It is intended to become a user-extensible replacement for StandardFirmata, without
the complexity of Firmata.

Feature Punch List

|           Feature          	|         Example         	|  Status  	|   Phase   |
|:--------------------------:	|:-----------------------:	|:--------:	|:--------:	|
| Debug Support              	| loop_back.py            	| Complete 	| Phase 1   |
| Analog Input               	| analog_input.py         	| Complete 	| Phase 1   |
| Digital Input              	| digital_input.py        	| Complete 	| Phase 1   |
| Digital Input Pullup       	| digital_input_pullup.py 	| Complete 	| Phase 1   |
| Digital Output             	| blink.py                	| Complete 	| Phase 1   |
| PWM Output (analog output) 	| fade.py                 	| Complete 	| Phase 1   |
| Servo                      	| servo.py               	| Complete 	| Phase 2   |
| i2c                        	| i2c_adxl345_accelerometer.py | Complete  | Phase 3 |
| HC-SR04                    	|                         	| TBD      	|
| DHT                        	|                         	| TBD      	|

It is early stages of this project, so there are may be some bugs lurking.
A word about the current directory structure. The code in the "phase" directories
contain the latest code, examples and arduino sketch. As the phases progress through
development each phase will contain the contents of the previous phase as well as the
additions for the phase itself.

Arduino-telemetrix is the Arduino server sketch, and telemetrix is the python client.

Python API for phase 3 may be found [here](https://htmlpreview.github.com/?https://github.com/MrYsLab/telemetrix/blob/master/phase3/api/index.html)) 

The code outside of the phase directories is likely to be highly volatile and should
be used with caution.

The project will be documented on my [Bots In Pieces blog.](https://mryslab.github.io/bots-in-pieces/index.html)
Here is a link to the [first installment.](https://mryslab.github.io/bots-in-pieces/arduino,stm32,firmata/2020/09/20/telemetrix-phase-1.html)

If you find bugs or would like to comment on the features, please enter an issue
 [here.](https://github.com/MrYsLab/telemetrix/issues)