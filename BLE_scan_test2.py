# ESP32からのブロードキャストをスキャンし続ける。
# ブロードキャストパケット内に格納されているスティックやボタンの入力情報
# を取り出す。


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
    
    # devにはアドバタイズパケットの情報が詰まっている。ScanEntryクラス
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr == '30:ae:a4:0e:4f:12':
            #print('welcome Advertise Data')
            advdata = dev.getScanData()
            #print(advdata)
            for (at, at_desc, ad) in advdata:
                if at == 0xff:  # ESP側でセットしたManifacturer Specific Data
                    mdata = int(ad, 16) # AD部分には16進文字列が格納されているため数値に変換
                    stick1_lr = (mdata & 0x000000ff00000000) >> 0x20
                    stick1_ud = (mdata & 0x00000000ff000000) >> 0x18
                    stick2_lr = (mdata & 0x0000000000ff0000) >> 0x10
                    stick2_ud = (mdata & 0x000000000000ff00) >> 0x08
            print(stick1_lr, stick1_ud, stick2_lr, stick2_ud)

# Scannerインスタンスを生成するとスキャン開始
# withDelegateでデバイス見つけたときのハンドラーを渡しておくと呼んでくれる。
scanner = Scanner().withDelegate(ScanDelegate())
try:
    while True:
        scanner.scan(0.05)

except KeyboardInterrupt:
    pass
