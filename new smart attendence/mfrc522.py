"""
MicroPython MFRC522 RFID Library for ESP32
"""

from machine import Pin, SPI
import time

class MFRC522:
    OK = 0
    NOTAGERR = 1
    ERR = 2
    
    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61
    
    def __init__(self, sck, mosi, miso, rst, cs):
        self.sck = sck
        self.mosi = mosi
        self.miso = miso
        self.rst = rst
        self.cs = cs
        
        self.rst.value(0)
        self.cs.value(1)
        
        self.spi = SPI(1, baudrate=1000000, polarity=0, phase=0, sck=self.sck, mosi=self.mosi, miso=self.miso)
        
        self.rst.value(1)
        self.init()
    
    def _write_reg(self, reg, value):
        self.cs.value(0)
        self.spi.write(bytes([0x80 | reg]))
        self.spi.write(bytes([value]))
        self.cs.value(1)
    
    def _read_reg(self, reg):
        self.cs.value(0)
        self.spi.write(bytes([0x80 & reg]))
        val = self.spi.read(1)
        self.cs.value(1)
        return val[0]
    
    def _set_bit_mask(self, reg, mask):
        tmp = self._read_reg(reg)
        self._write_reg(reg, tmp | mask)
    
    def _clear_bit_mask(self, reg, mask):
        tmp = self._read_reg(reg)
        self._write_reg(reg, tmp & (~mask))
    
    def request(self, mode):
        """Request for a card"""
        self._write_reg(0x0D, 0x07)
        self._write_reg(0x01, 0x40)
        
        self.cs.value(0)
        self.spi.write(bytes([0x26, 0x07]))
        self.cs.value(1)
        
        time.sleep_ms(10)
        
        self.cs.value(0)
        self.spi.read(2)
        valid = self.spi.read(1)[0]
        self.cs.value(1)
        
        if valid == 0x16:
            return (self.OK, None)
        else:
            return (self.NOTAGERR, None)
    
    def anticoll(self):
        """Anti-collision detection"""
        self._write_reg(0x09, 0x00)
        self._write_reg(0x01, 0x40)
        self._write_reg(0x05, 0x00)
        self._write_reg(0x06, 0x00)
        self._write_reg(0x09, 0x93)
        
        self.cs.value(0)
        self.spi.write(bytes([0x93, 0x20]))
        
        uid = []
        for i in range(4):
            uid.append(self.spi.read(1)[0])
        
        crc = []
        for i in range(2):
            crc.append(self.spi.read(1)[0])
        
        self.cs.value(1)
        
        return (self.OK, uid)
    
    def select_tag(self, uid):
        """Select a tag"""
        self._write_reg(0x09, 0x00)
        self._write_reg(0x01, 0x40)
        self._write_reg(0x05, 0x00)
        self._write_reg(0x06, 0x00)
        self._write_reg(0x09, 0x93)
        
        self.cs.value(0)
        self.spi.write(bytes([0x93, 0x70]))
        
        for byte in uid:
            self.spi.write(bytes([byte]))
        
        crc = self.spi.read(2)
        self.cs.value(1)
        
        time.sleep_ms(10)
        self.cs.value(0)
        resp = self.spi.read(1)[0]
        self.cs.value(1)
        
        if resp == 0x0A:
            return self.OK
        else:
            return self.ERR
    
    def stop_crypto1(self):
        """Stop encryption"""
        self._clear_bit_mask(0x08, 0x08)
    
    def init(self):
        """Initialize MFRC522"""
        # Reset
        self._write_reg(0x01, 0x0F)
        
        # Set timer
        self._write_reg(0x02, 0x29)
        self._write_reg(0x03, 0x00)
        
        # Set FIFO
        self._write_reg(0x04, 0x00)
        
        # Set IRQ
        self._write_reg(0x07, 0x80)
        
        # Set CRC
        self._write_reg(0x05, 0x00)
        self._write_reg(0x06, 0x00)
        
        # Set mode
        self._write_reg(0x08, 0x08)
        
        # Set TxControl
        self._write_reg(0x0C, 0x00)
        
        # Set RxControl
        self._write_reg(0x0D, 0x00)
        
        # Set CommandReg
        self._write_reg(0x01, 0x20)
        
        # Set ComIEnReg
        self._write_reg(0x02, 0x00)
        
        # Set DivIEnReg
        self._write_reg(0x03, 0x00)
        
        # Set ComIrqReg
        self._write_reg(0x04, 0x00)
        
        # Set DivIrqReg
        self._write_reg(0x05, 0x00)
        
        # Set FIFODataReg
        self._write_reg(0x06, 0x00)
        
        # Set FIFOLevelReg
        self._write_reg(0x07, 0x00)
        
        # Set WaterLevelReg
        self._write_reg(0x08, 0x00)
        
        # Set ControlReg
        self._write_reg(0x09, 0x00)
        
        # Set BitFramingReg
        self._write_reg(0x0A, 0x00)
        
        # Set CollReg
        self._write_reg(0x0B, 0x00)
        
        # Set ModeReg
        self._write_reg(0x0C, 0x00)
        
        # Set TxModeReg
        self._write_reg(0x0D, 0x00)
        
        # Set RxModeReg
        self._write_reg(0x0E, 0x00)
        
        # Set TxControlReg
        self._write_reg(0x0F, 0x00)
        
        # Set TxASKReg
        self._write_reg(0x10, 0x00)
        
        # Start
        self._write_reg(0x01, 0x20)
        self._write_reg(0x0A, 0x80)