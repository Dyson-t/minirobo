# -*- coding: utf-8 -*-
import sys
from time import sleep
import smbus
import math

MAX_UD = 80
MAX_LR = 90

class CameraHead:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.address_pca9685 = 0x40
        self.bus.write_byte_data(self.address_pca9685, 0x00, 0x00)
        self.setPCA9685Freq(50)
        self.current_x = 0              # 現在のX軸角度 
        self.current_y = 0              # 現在のY軸角度
    
    def setPCA9685Freq(self, freq):
        freq = 0.9*freq # Arduinoのライブラリより
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = int(math.floor(prescaleval + 0.5))
        oldmode = self.bus.read_byte_data(self.address_pca9685, 0x00)
        newmode = (oldmode & 0x7F) | 0x10             # スリープモード
        self.bus.write_byte_data(self.address_pca9685, 0x00, newmode) # スリープモードへ
        self.bus.write_byte_data(self.address_pca9685, 0xFE, prescale) # プリスケーラーをセット
        self.bus.write_byte_data(self.address_pca9685, 0x00, oldmode)
        sleep(0.005)
        self.bus.write_byte_data(self.address_pca9685, 0x00, oldmode | 0xa1)
    
    def setPCA9685Duty(self, channel, on, off):
        channelpos = 0x6 + 4*channel
        try:
            self.bus.write_i2c_block_data(self.address_pca9685, channelpos, [on&0xFF, on>>8, off&0xFF, off>>8] )
        except IOError:
            pass
    
    def setSurboAngle(self, channel, angle):
        duty = int( ( ( 410 - 142 ) / 170 ) * angle ) + 310
        #duty = ( ( ( 410 - 142 ) / 170 ) * angle ) + 310
        self.setPCA9685Duty( channel, 0, duty )
    
    # 絶対角度指定
    def moveCameraHead(self, tiltlr, tiltud):
        self.setSurboAngle(0, tiltud)
        self.setSurboAngle(1, tiltlr)
        self.current_x = tiltlr
        self.current_y = tiltud
    
    # 相対角度指定
    def moveCameraHeadRel(self, tiltlr, tiltud):
        self.current_x += tiltlr
        self.current_y += tiltud
        if self.current_x >= MAX_LR:
            self.current_x = 90
        if self.current_x <= -1 * MAX_LR:
            self.current_x = -90
        if self.current_y >= MAX_UD:
            self.current_y = 90
        if self.current_y <= -1 * MAX_UD:
            self.current_y = -90
        self.setSurboAngle(0, self.current_y)
        self.setSurboAngle(1, self.current_x)
