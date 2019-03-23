# ESP32からのブロードキャストをスキャンせず、直接コネクトする。
# ノーティファイを待ち続ける。
# ノーティファイされたデータを表示する。（モーター制御は次のステップ）

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
HANDLE_RSSI = 50 #0x0034

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
        print("handle=",cHandle, ":",c_data)
        datah = int(c_data, 16)
        if cHandle == HANDLE_STICK_R:
            stick1_lr = (datah & 0xffff0000) >> 0x10
            stick1_ud = (datah & 0x0000ffff)
            print("stick1_lr = ", stick1_lr, " stick1_ud=", stick1_ud)
        if cHandle == HANDLE_STICK_L:
            stick2_lr = (datah & 0xffff0000) >> 0x10
            stick2_ud = (datah & 0x0000ffff)
            print("stick2_lr = ", stick2_lr, " stick2_ud=", stick2_ud)
        if cHandle == HANDLE_BUTTON1:
            button1 = (datah & 0xff000000) >> 0x18
        if cHandle == HANDLE_BUTTON2:
            button2 = (datah & 0xff000000) >> 0x18


# スキャンしてデバイス見つけたときのハンドラー
# class ScanDelegate(DefaultDelegate):
#     def __init__(self):
#         DefaultDelegate.__init__(self)
#         self.lastseq = None
#         self.lasttime = datetime.fromtimestamp(0)
    
#     def handleDiscovery(self, dev, isNewDev, isNewData):
#         if dev.addr == ADDR_BSTICK: # ESP32 からだったら
#             bstick = Connection(ADDR_BSTICK)
#             bstick.setDelegate(NotifyDelegate())
#             while True:
#                 if bstick.waitForNotifications(1.0):
#                     continue
#                 print("wait..")



            

# # Scannerインスタンスを生成するとスキャン開始
# # withDelegateでデバイス見つけたときのハンドラーを渡しておくと呼んでくれる。
# scanner = Scanner().withDelegate(ScanDelegate())
# try:
#     while True:
#         scanner.scan(0.05)

try:
    bstick = Connection(ADDR_BSTICK)
    bstick.setDelegate(NotifyDelegate())
    while True:
        if bstick.waitForNotifications(10.0):
            continue
        print("wait..")


except KeyboardInterrupt:
    pass
