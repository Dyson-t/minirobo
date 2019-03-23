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
HANDLE_STICK_R = 42
HANDLE_STICK_L = 44
HANDLE_BUTTON1 = 46
HANDLE_BUTTON2 = 48

# Bstick へコネクトするためのクラス（Peripheralクラスを継承）
# インスタンスを生成した時点でコネクトしてくれる。（たぶん・・・）
class Bstick(Peripheral):
    def __init__(self, addr):
        Peripheral.__init__(self, addr, addrType="public")

# Notify受信したときのハンドラー
class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        print("handle=", cHandle, ":0x",binascii.b2a_hex(data))



# スキャンしてデバイス見つけたときのハンドラー
# class ScanDelegate(DefaultDelegate):
#     def __init__(self):
#         DefaultDelegate.__init__(self)
#         self.lastseq = None
#         self.lasttime = datetime.fromtimestamp(0)
    
#     def handleDiscovery(self, dev, isNewDev, isNewData):
#         if dev.addr == ADDR_BSTICK: # ESP32 Bstickからだったら
#             bstick = Bstick(ADDR_BSTICK)
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
    bstick = Bstick(ADDR_BSTICK)
    bstick.setDelegate(NotifyDelegate())
    while True:
        if bstick.waitForNotifications(10.0):
            continue
        print("wait..")


except KeyboardInterrupt:
    pass
