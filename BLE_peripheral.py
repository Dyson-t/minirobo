# ESP32とコネクトし、ノーティファイを待ち続ける。
# ノーティファイされたデータに従い、カメラヘッドを動かす。足回りは未実装
# このコードが最もシンプルにノーティファイを受け取る方法だと思われる。
# ポイント
# ・スキャンをすっとばしていきなりコネクトする。（相手のアドレスがわかっていればこれで良い）
# ・コネクトに失敗することがある。この場合、成功するまでこのコードを再実行すること。
# ・いきなり接続が切れることがある。これがESP起因なのかbluepy起因なのかは調査中。

from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import sys
import struct
from datetime import datetime
import argparse
import binascii
from PCA9685_test import setSurboAngle

ADDR_BSTICK = '30:ae:a4:0e:4f:12'
HANDLE_STICKS = 42
HANDLE_BUTTON1 = 46
HANDLE_BUTTON2 = 48

#キャラクタリスティック値からサーボ角度への変換
# charactaristic は今回の環境の場合、おおよそ 0x00 〜 0xd4 の値を取る。センターは0x61である。
# これを -90度 〜 +90度 となるよう変換する。
def c2tilt( chr ):
    maxtilt = 90
    #0xc2以上は0xc2とみなす。
    mchr = chr
    if mchr > 0xc2:
        mchr = 0xc2
    mchr = mchr - 0x61 # -0x61 〜 0x61 の範囲へ補正x
    tilt = int(( mchr / 0x61 ) * maxtilt * -1 ) 
    return tilt

def moveCameraHead(tiltlr, tiltud):
    setSurboAngle(0, tiltud)
    setSurboAngle(1, tiltlr)

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
        c_data = binascii.b2a_hex(data)
        #c_handle = binascii.b2a_hex(cHandle)
        if cHandle == HANDLE_STICKS:
            datah = int(c_data, 16)
            stick1_lr = (datah & 0xff000000) >> 0x18
            stick1_ud = (datah & 0x00ff0000) >> 0x10
            stick2_lr = (datah & 0x0000ff00) >> 0x08
            stick2_ud = (datah & 0x000000ff)
            
            # カメラヘッドを動かす
            moveCameraHead(c2tilt(stick1_lr), c2tilt(stick1_ud))

try:
    bstick = Bstick(ADDR_BSTICK)
    bstick.setDelegate(NotifyDelegate())
    while True:
        if bstick.waitForNotifications(10.0):
            continue
        print("wait..")

except KeyboardInterrupt:
    pass
