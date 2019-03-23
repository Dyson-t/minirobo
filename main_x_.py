# BLE_connect.pyをベースにさらに改修。スキャン→コネクトするようにした。
# 2019/3/21：なぜかスキャン時のハンドラーからコネクトしようとすると異常
# 終了する。前はうまく動いてたのに。。。
from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import sys
import struct
from datetime import datetime
import argparse
import binascii

ADDR_BSTICK = '30:ae:a4:0e:4f:12'
HANDLE_STICK_R = 42 #0x002a
HANDLE_STICK_L = 44 #0x002c
HANDLE_BUTTON1 = 46 #0x0030
HANDLE_BUTTON2 = 48 #0x0032
HANDLE_RSSI    = 50 #0x0034

# ペリフェラルへコネクトするためのクラス（Peripheralクラスを継承）
# インスタンスを生成した時点でコネクトしてくれる。
class Connection(Peripheral):
    def __init__(self, addr):
        Peripheral.__init__(self, addr, addrType="public")

# Notify受信したときのハンドラー
class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        c_data = binascii.b2a_hex(data)
        # print("handle=",cHandle, ":",c_data)
        datah = int(c_data, 16)
        if cHandle == HANDLE_STICK_R:
            stick1_lr = (datah & 0xffff0000) >> 0x10
            stick1_ud = (datah & 0x0000ffff)
            print("RStick:lr = ", stick1_lr, " ud=", stick1_ud)
        if cHandle == HANDLE_STICK_L:
            stick2_lr = (datah & 0xffff0000) >> 0x10
            stick2_ud = (datah & 0x0000ffff)
            print("LStick:lr = ", stick2_lr, " ud=", stick2_ud)
        if cHandle == HANDLE_BUTTON1:
            button1 = (datah & 0xff000000) >> 0x18
        if cHandle == HANDLE_BUTTON2:
            button2 = (datah & 0xff000000) >> 0x18

#スキャンしてデバイス見つけたときのハンドラー
class ScanDelegate(DefaultDelegate):
     def __init__(self):
         DefaultDelegate.__init__(self)
         self.lastseq = None
         self.lasttime = datetime.fromtimestamp(0)
    
     def handleDiscovery(self, dev, isNewDev, isNewData):
         if dev.addr == ADDR_BSTICK: # ESP32 からだったら
             print("try connect to ", dev.addr )
             con = Connection(ADDR_BSTICK)
             print("connected." )
             con.setDelegate(NotifyDelegate())
             while True:
                 if con.waitForNotifications(10.0):
                     continue
                 print("wait..")

# Scannerインスタンスを生成するとスキャン開始
# withDelegateでデバイス見つけたときのハンドラーを渡しておくと呼んでくれる。
scanner = Scanner().withDelegate(ScanDelegate())
try:
    while True:
        print("scanning..")
        scanner.scan(1)
        sleep(1)

except KeyboardInterrupt:
    pass
