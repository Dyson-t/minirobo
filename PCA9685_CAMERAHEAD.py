# -*- coding: utf-8 -*-
import sys
from time import sleep
import smbus
import math

def resetPCA9685():
    bus.write_byte_data(address_pca9685, 0x00, 0x00)

def setPCA9685Freq(freq):
    freq = 0.9*freq # Arduinoのライブラリより
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    prescale = int(math.floor(prescaleval + 0.5))
    oldmode = bus.read_byte_data(address_pca9685, 0x00)
    newmode = (oldmode & 0x7F) | 0x10             # スリープモード
    bus.write_byte_data(address_pca9685, 0x00, newmode) # スリープモードへ
    bus.write_byte_data(address_pca9685, 0xFE, prescale) # プリスケーラーをセット
    bus.write_byte_data(address_pca9685, 0x00, oldmode)
    sleep(0.005)
    bus.write_byte_data(address_pca9685, 0x00, oldmode | 0xa1)

def setPCA9685Duty(channel, on, off):
    channelpos = 0x6 + 4*channel
    try:
        bus.write_i2c_block_data(address_pca9685, channelpos, [on&0xFF, on>>8, off&0xFF, off>>8] )
    except IOError:
        pass

def setSurboAngle(channel, angle):
    duty = int( ( ( 410 - 142 ) / 170 ) * angle ) + 310
    #duty = ( ( ( 410 - 142 ) / 170 ) * angle ) + 310
    setPCA9685Duty( channel, 0, duty )

def moveCameraHead(tiltlr, tiltud):
    setSurboAngle(0, tiltud)
    setSurboAngle(1, tiltlr)

bus = smbus.SMBus(1)
address_pca9685 = 0x40

resetPCA9685()
setPCA9685Freq(50)

if __name__ == "__main__":
    #縦横の角度をもらってそのとおりに動かす
    #angle_h = int(sys.argv[1])
    #angle_v = int(sys.argv[2])
    #setSurboAngle(0, angle_h)
    #setSurboAngle(1, angle_v)


    # どれだけ滑らかに動くかテスト
    angle_h = -50
    while angle_h < 50:
        setSurboAngle(0, angle_h)
        setSurboAngle(1, angle_h)
        angle_h += 0.05

