"""
MicroPython SSD1306 OLED Driver
"""

from machine import Pin, SoftI2C
import time

class SSD1306_I2C:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.buffer = bytearray(width * height // 8)
        self.init_display()
    
    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytes([0x00, cmd]))
    
    def write_data(self, data):
        self.i2c.writeto(self.addr, bytes([0x40]) + data)
    
    def init_display(self):
        self.write_cmd(0xAE)  # Display off
        self.write_cmd(0xD5)  # Set display clock divide ratio
        self.write_cmd(0x80)  # Suggested ratio
        self.write_cmd(0xA8)  # Set multiplex
        self.write_cmd(0x3F)  # 64 lines
        self.write_cmd(0xD3)  # Set display offset
        self.write_cmd(0x00)  # No offset
        self.write_cmd(0x40)  # Set start line
        self.write_cmd(0x8D)  # Charge pump
        self.write_cmd(0x14)  # Enable charge pump
        self.write_cmd(0x20)  # Memory addressing mode
        self.write_cmd(0x00)  # Horizontal
        self.write_cmd(0xA1)  # Segment remap
        self.write_cmd(0xC8)  # COM scan direction
        self.write_cmd(0xDA)  # COM pins hardware
        self.write_cmd(0x12)
        self.write_cmd(0x81)  # Contrast
        self.write_cmd(0xCF)
        self.write_cmd(0xD9)  # Pre-charge period
        self.write_cmd(0xF1)
        self.write_cmd(0xDB)  # VCOM detect
        self.write_cmd(0x40)
        self.write_cmd(0xA4)  # Resume to RAM content
        self.write_cmd(0xA6)  # Normal display
        self.write_cmd(0x2E)  # Deactivate scroll
        self.write_cmd(0xAF)  # Display on
    
    def fill(self, color):
        """Fill entire screen with color (0=black, 1=white)"""
        fill_byte = 0xFF if color else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = fill_byte
    
    def pixel(self, x, y, color):
        """Set pixel at (x,y) to color (0=black, 1=white)"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        index = x + (y // 8) * self.width
        bit = 1 << (y % 8)
        if color:
            self.buffer[index] |= bit
        else:
            self.buffer[index] &= ~bit
    
    def text(self, text, x, y, color=1):
        """Draw text on screen"""
        for i, char in enumerate(text):
            if char == '\n':
                x = 0
                y += 10
                continue
            self.char(char, x + i*6, y, color)
    
    def char(self, char, x, y, color=1):
        """Draw a single character"""
        # Simplified font - just draw a rectangle for testing
        # For full font, you would include a font array here
        if char == ' ':
            return
        for i in range(5):
            if x + i < self.width and y < self.height:
                self.pixel(x + i, y, color)
                self.pixel(x + i, y + 5, color)
        if x < self.width:
            self.pixel(x, y + 1, color)
            self.pixel(x, y + 2, color)
            self.pixel(x, y + 3, color)
            self.pixel(x + 4, y + 1, color)
            self.pixel(x + 4, y + 2, color)
            self.pixel(x + 4, y + 3, color)
    
    def show(self):
        """Update display with buffer contents"""
        for page in range(self.height // 8):
            self.write_cmd(0xB0 + page)  # Set page address
            self.write_cmd(0x00)         # Set lower column address
            self.write_cmd(0x10)         # Set higher column address
            start = page * self.width
            end = start + self.width
            self.write_data(self.buffer[start:end])