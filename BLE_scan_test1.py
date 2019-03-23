# ESP32からのブロードキャストをスキャンし続ける。
# ブロードキャストパケット内に格納されているスティックやボタンの入力情報
# を取り出し、ロボを制御する。

from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import sys
import struct
from datetime import datetime
import argparse

# スキャンしてデバイス見つけたときのハンドラー
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.lastseq = None
        self.lasttime = datetime.fromtimestamp(0)
    
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print( 'found new dev (%s)' % dev.addr)

# Scannerインスタンスを生成するとスキャン開始
# withDelegateでデバイス見つけたときのハンドラーを渡しておくと呼んでくれる。
scanner = Scanner().withDelegate(ScanDelegate())
try:
    while True:
        scanner.scan(10.0)

except KeyboardInterrupt:
    pass




        

