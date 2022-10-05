import sys
import time
from telemetrix import telemetrix

"""
This file contains a library to control an i2c LCD. 
See i2c_ldc_pcf8574_hello_world.py for an example of its use.
"""


class _OutputState(object):
    """
       This class helps us construct the I2C output based on data and control outputs.
       Because the LCD is set to 4-bit mode, 4 bits of the I2C output are for the control outputs
       while the other 4 bits are for the 8 bits of data which are send in parts using
       the enable output.
    """
    def __init__(self):
        self.rs = 0
        self.rw = 0
        self.E = 0
        self.Led = 0
        self.data = 0

    def GetLowData(self):
        buffer = self.rs
        buffer |= self.rw << 1
        buffer |= self.E << 2
        buffer |= self.Led << 3
        buffer |= (self.data & 0x0F) << 4

        return buffer

    def GetHighData(self):
        buffer = self.rs
        buffer |= self.rw << 1
        buffer |= self.E << 2
        buffer |= self.Led << 3
        buffer |= (self.data & 0xF0)

        return buffer


class LcdI2c(object):
    """
    This class contains all the LCD control methods that constitute the API.
    """
    def __init__(self, board, address=0x27, columns=16, rows=2):
        """
        Initializer for an LcdI2c class

        :param board: a telemetrix instance

        :param address: I2C address of the LCD

        :param columns: Number of display columns

        :param rows: Number of display rows
        """
        self.board = board
        self._address = address
        self._columnMax = columns - 1
        self._rowMax = rows - 1
        self._displayState = 0x00
        self._entryState = 0x00
        self._output = _OutputState()

        board.set_pin_mode_i2c()
        board.i2c_write(self._address, [0])

    def begin(self):
        """
        Initialize the LCD display
        """
        self._delayMilliseconds(50)  # Wait more than 40ms after powerOn.
        self._I2C_Write(0b00000000)  # Clear i2c adapter
        self._delayMilliseconds(50)  # Wait more than 40ms after powerOn.

        self._InitializeLCD()

    def backlight(self):
        """
        Turn on the backlight
        """
        self._output.Led = 1
        # Led pin is independent of LCD data and control lines.
        self._I2C_Write(0b00000000 | self._output.Led << 3)

    def noBacklight(self):
        """
        Turn off the backlight
        """
        self._output.Led = 0
        # Led pin is independent of LCD data and control lines.
        self._I2C_Write(0b00000000 | self._output.Led << 3)

    def clear(self):
        """
        Clear the display
        """
        self._output.rs = 0
        self._output.rw = 0

        self._LCD_Write(0b00000001)
        self._delayMilliseconds(160)

    def home(self):
        """
        Set the cursor to the home position
        """
        self._output.rs = 0
        self._output.rw = 0

        self._LCD_Write(0b00000010)
        self._delayMilliseconds(160)

    # Part of Entry mode set
    def leftToRight(self):
        """
        Set display data entry from left to right
        """
        self._output.rs = 0
        self._output.rw = 0

        self._entryState |= 1 << 1

        self._LCD_Write(0b00000100 | self._entryState)
        self._delayMilliseconds(37)

    # Part of Entry mode set
    def rightToLeft(self):
        """
        Set display data entry from right to left
        """
        self._output.rs = 0
        self._output.rw = 0

        self._entryState &= ~(1 << 1)

        self._LCD_Write(0b00000100 | self._entryState)
        self._delayMilliseconds(37)

    # Part of Entry mode set
    def autoscroll(self):
        """
        Turn on display autoscroll
        """
        self._output.rs = 0
        self._output.rw = 0

        self._entryState |= 1

        self._LCD_Write(0b00000100 | self._entryState)
        self._delayMilliseconds(37)

    # Part of Entry mode set
    def noAutoscroll(self):
        """
        Turn off display autoscroll
        """
        self._output.rs = 0
        self._output.rw = 0

        self._entryState &= ~1

        self._LCD_Write(0b00000100 | self._entryState)
        self._delayMilliseconds(37)

    # Part of Display control
    def display(self):
        """
        Enable the display
        """
        self._output.rs = 0
        self._output.rw = 0

        self._displayState |= 1 << 2

        self._LCD_Write(0b00001000 | self._displayState)
        self._delayMilliseconds(37)

    # Part of Display control
    def noDisplay(self):
        """
        Disable the display
        """
        self._output.rs = 0
        self._output.rw = 0

        self._displayState &= ~(1 << 2)

        self._LCD_Write(0b00001000 | self._displayState)
        self._delayMilliseconds(37)

    # Part of Display control
    def cursor(self):
        """
        Enable the cursor
        """
        self._output.rs = 0
        self._output.rw = 0

        self._displayState |= 1 << 1

        self._LCD_Write(0b00001000 | self._displayState)
        self._delayMilliseconds(37)

    # Part of Display control
    def noCursor(self):
        """
        Disable the cursor
        """
        self._output.rs = 0
        self._output.rw = 0

        self._displayState &= ~(1 << 1)

        self._LCD_Write(0b00001000 | self._displayState)
        self._delayMilliseconds(37)

    # Part of Display control
    def blink(self):
        """
        Enable blink
        """
        self._output.rs = 0
        self._output.rw = 0

        self._displayState |= 1

        self._LCD_Write(0b00001000 | self._displayState)
        self._delayMilliseconds(37)

    # Part of Display control
    def noBlink(self):
        """
        Disable blink
        """
        self._output.rs = 0
        self._output.rw = 0

        self._displayState &= ~1

        self._LCD_Write(0b00001000 | self._displayState)
        self._delayMilliseconds(37)

    # Part of Cursor or display shift
    def scrollDisplayLeft(self):
        """
        Scroll the display to the left
        """
        self._output.rs = 0
        self._output.rw = 0

        self._LCD_Write(0b00011000)
        self._delayMilliseconds(37)

    # Part of Cursor or display shift
    def scrollDisplayRight(self):
        """
        Scroll the display to the right
        """

        self._output.rs = 0
        self._output.rw = 0

        self._LCD_Write(0b00011100)
        self._delayMilliseconds(37)

    # Set CGRAM address
    def createChar(self, location, charmap=[]):
        """
        Create a custom character

        :param location: integer identifier of the custom character

        :param charmap: Each character is made up of a 5x8 bitmap
        """
        self._output.rs = 0
        self._output.rw = 0

        location %= 8

        self._LCD_Write(0b01000000 | (location << 3))
        self._delayMilliseconds(37)

        for i in charmap:
            self.write(i)

        self.setCursor(0, 0)  # Set the address pointer back to the DDRAM

    # Set DDRAM address
    def setCursor(self, col, row):
        """
        Set the cursor to the column and row
        :param col: display column
        :param row: display row
        """
        row_offsets = []
        row_offsets.extend([0x00, 0x40, 0x14, 0x54])
        self._output.rs = 0
        self._output.rw = 0

        if col > self._columnMax:
            col = self._columnMax  # sanity limits
        if row > self._rowMax:
            row = self._rowMax  # sanity limits

        newAddress = row_offsets[row] + col

        self._LCD_Write(0b10000000 | newAddress)
        self._delayMilliseconds(37)

    def write(self, character):
        """
        Wrtie a custom character to the display
        :param character: The custom character ID
        """
        self._output.rs = 1
        self._output.rw = 0

        self._LCD_Write(character)
        self._delayMilliseconds(41)

        return 1

    def _InitializeLCD(self):
        """
        Initialize the i2c interface and LCD to a known state
        """
        # See HD44780U datasheet "Initializing by Instruction" Figure 24 (4-Bit Interface)
        self._output.rs = 0
        self._output.rw = 0

        self._LCD_Write(0b00110000, True)
        self._delayMilliseconds(42)
        self._LCD_Write(0b00110000, True)
        self._delayMilliseconds(150)
        self._LCD_Write(0b00110000, True)
        self._delayMilliseconds(37)
        self._LCD_Write(0b00100000, True)  # Function Set - 4 bits mode
        self._delayMilliseconds(37)
        self._LCD_Write(0b00101000)  # Function Set - 4 bits(Still), 2 lines, 5x8 font
        self._delayMilliseconds(37)

        self.display()
        self.clear()
        self.leftToRight()

    def _I2C_Write(self, output):
        self.board.i2c_write(self._address, [output])

    def _LCD_Write(self, output, initialization=False):
        self._output.data = output

        self._output.E = True
        self._I2C_Write(self._output.GetHighData())
        self._delayMicroseconds(1)  # High part of enable should be >450 nS

        self._output.E = False
        self._I2C_Write(self._output.GetHighData())

        # During initialization, we only send half a byte
        if not initialization:
            # I think we need a delay between half byte writes,
            # but no sure how long it needs to be.
            self._delayMicroseconds(37)

            self._output.E = True
            self._I2C_Write(self._output.GetLowData())
            self._delayMicroseconds(1)  # High part of enable should be >450 nS

            self._output.E = False
            self._I2C_Write(self._output.GetLowData())
        # self._delayMicroseconds(37) # Some commands have different timing requirement,
        # so every command should handle its own delay after execution

    def _delayMicroseconds(self, microsec):
        time.sleep(microsec * 1e-6)

    def _delayMilliseconds(self, Millisec):
        time.sleep(Millisec * 1e-3)

    def print(self, text):
        """
        Print a string to the display

        :param text: A string of text

        """
        for c in bytearray(text, 'ASCII'):
            self.write(c)
