"""
 Copyright (c) 2023 Pierre Jeunesse All rights reserved.

 https://github.com/PierreJeunesse

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

"""
This example sets up and control an MCP9600 i2c Thermocouple.
The structure is the same as MCP9600_basic_demo.ino provided by the manufacturer Seeed.
It will continuously print data from the device.
"""
import sys
import time

from telemetrix import telemetrix


# the call back function to print the MCP9600 data
def the_callback(data):
    """

    :param data: [Device address, device read register, data]
    :return:
    """

    first_byte = data[5]
    sec_byte = data[6]
    Temp_ = ((first_byte << 8) | sec_byte) / 16

    # Display result
    print(Temp_)


def mpc9600(my_board):
    # setup mpc9600
    # device address = 96
    my_board.set_pin_mode_i2c()  # #define DEFAULT_IIC_ADDR  0X60 (in Seeed_MCO9600.h)

    # err_t sensor_basic_config() {
    #     err_t ret = NO_ERROR;
    #     CHECK_RESULT(ret, sensor.set_filt_coefficients(FILT_MID)); (in Seeed_MCO9600.cpp)
    #           IIC_read_byte(THERM_SENS_CFG_REG_ADDR, &therm_cfg_data) (in Seeed_MCO9600.cpp)
    #               THERM_SENS_CFG_REG_ADDR : 0X5 => 5 (in Seeed_MCO9600.h)
    #               FILT_MID : 4 (in Seeed_MCO9600.h)
    my_board.i2c_write(96, [5, 4])
    time.sleep(1)

    #     CHECK_RESULT(ret, sensor.set_cold_junc_resolution(COLD_JUNC_RESOLUTION_0_25));
    #           same logic as above
    my_board.i2c_write(96, [6, 1 << 7])
    time.sleep(1)

    #     CHECK_RESULT(ret, sensor.set_ADC_meas_resolution(ADC_14BIT_RESOLUTION));
    my_board.i2c_write(96, [6, 1 << 5])
    time.sleep(1)

    #     CHECK_RESULT(ret, sensor.set_burst_mode_samp(BURST_32_SAMPLE));
    my_board.i2c_write(96, [6, 0 << 2])
    time.sleep(1)

    #     CHECK_RESULT(ret, sensor.set_sensor_mode(NORMAL_OPERATION));
    my_board.i2c_write(96, [6, 0])
    time.sleep(1)

    while True:
        # read 2 bytes from the data register
        try:
            my_board.i2c_read_restart_transmission(96, 0, 2, the_callback, i2c_port=0,
                                                   write_register=True)
            time.sleep(0.5)

        except (KeyboardInterrupt, RuntimeError):
            my_board.shutdown()
            sys.exit(0)


board = telemetrix.Telemetrix()
try:
    mpc9600(board)
except KeyboardInterrupt:
    board.shutdown()
    sys.exit(0)
