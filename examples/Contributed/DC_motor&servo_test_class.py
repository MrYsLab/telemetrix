import sys
import time

from telemetrix import telemetrix

# set arduino pins acoording to L298N motor driver outputs
ANALOG_PIN = 3  # enA
ANALOG_PIN = 9  # enB
DIGITAL_PIN = 4  # in1
DIGITAL_PIN = 5  # in2
DIGITAL_PIN = 6  # in3
DIGITAL_PIN = 7  # in4
SERVO_PIN = 12

# first motor controlled by (enA,in1,in2) -> (3, 4, 5) pins
# second motor controlled by (enB,in3,in4) -> (9, 6, 7) pins


class wheels():
    def __init__(self):
        # some globals
        # Create a Telemetrix instance.
        self.board = telemetrix.Telemetrix()
        # attach servo pin
        self.board.set_pin_mode_servo(SERVO_PIN, 900, 2000)
        # set speed of DC motors
        self.speed = 255  # min: 8 - max: 255

    def run(self):
        self.dcTest()
        self.servoTest()

    def set_speed(self):
        # setting same speed for both motors for sync movement (check current voltage for both motors to be sure they are sync )
        self.board.analog_write(3, self.speed)  # Analog Pin Write
        self.board.analog_write(9, self.speed)  # Analog Pin Write

    def car_forward(self):
        self.board.digital_write(4, 1)
        self.board.digital_write(5, 0)
        self.board.digital_write(6, 1)
        self.board.digital_write(7, 0)

    def car_backward(self):
        self.board.digital_write(4, 0)
        self.board.digital_write(5, 1)
        self.board.digital_write(6, 0)
        self.board.digital_write(7, 1)

    def car_left(self):
        self.board.digital_write(4, 1)
        self.board.digital_write(5, 0)
        self.board.digital_write(6, 0)
        self.board.digital_write(7, 1)

    def car_right(self):
        self.board.digital_write(4, 0)
        self.board.digital_write(5, 1)
        self.board.digital_write(6, 1)
        self.board.digital_write(7, 0)

    def stop(self):
        self.board.digital_write(4, 0)
        self.board.digital_write(5, 0)
        self.board.digital_write(6, 0)
        self.board.digital_write(7, 0)

    def servoTest(self):
        self.board.servo_write(SERVO_PIN, 0)
        time.sleep(1)
        self.board.servo_write(SERVO_PIN, 90)
        time.sleep(1)
        self.board.servo_write(SERVO_PIN, 180)
        time.sleep(1)
        self.board.servo_write(SERVO_PIN, 0)
        time.sleep(1)
        self.board.servo_detach(SERVO_PIN)

    def dcTest(self):
        self.set_speed()
        self.car_forward()
        time.sleep(3)
        self.stop()
        time.sleep(.2)
        self.car_backward()
        time.sleep(3)
        self.stop()
        time.sleep(.2)
        self.car_left()
        time.sleep(3)
        self.stop()
        time.sleep(.2)
        self.car_right()
        time.sleep(3)
        self.stop()
        time.sleep(.2)

    def shutDown(self):
        self.board.shutdown()


if __name__ == '__main__':
    wheels().run()
