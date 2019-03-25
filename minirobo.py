# ESP32とコネクトし、ノーティファイを待ち続ける。
# ノーティファイされたデータに従い、カメラヘッド、DCモーター動かす。
# 
# ポイント
# ■コネクト成功するまで自動リトライするようにしたい
# 　　仕掛け）Peripheralクラスを継承したConnectionクラスにThreadクラスも多重継承し、
#           別スレッドからつながるまでコネクトし続けるようにした。このやり方は
#           ambientのgithubを参考にした。
# ■接続断時に即座に再接続するようにした（scannedDevsの制御をやめた）
# ■ラズパイ起動時に自動起動するようにする。
# □コントロール側のVOLUMEでカメラのズームができるようにしたい。できるのか？
# □コントロール側のButton1でシャッター切れるようにしたい。
# □LCDに各種情報を表示するようにした。なお、LCDは他のコードからも使いたいので、サービス化した。
# ■いきなり接続が切れることがある。この対策として、ESP側は自動でAdvertiseに移行。
#  ラズパイ側は自動でScanに移行するようにする。
# ■RSSI値をScannerオブジェクトから取得して、ESP側へWRITEする
# □コントローラ側でシャットダウンできるようにしたい
# □カメラ画像画面をHUD風にしたい。各種センサー情報、ペリフェラル側の情報、
#                              収集した情報履歴、RSSI、BLEが途切れたときのための操作機能
# ■後退時に左右制御しにくい問題を修正
# ■駆動系を別ソース化
# □lcd.printをprintと同じように使えるようにしたい。変数埋め込みとか
# ■カメラヘッドの動きを滑らかにしたい。PWMの解像度UP → スティックのキャラクタリスティックを左右分割
# ■DCモーターのノイズでサーボが誤動作するのでコンデンサ追加したい（ハード側）→ 乾電池を交換することで解決。
# ■不意の接続断時にモーターが回り続ける事象の解決。緊急停止するようにした。

import RPi.GPIO as GPIO
from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import sys
import struct
from datetime import datetime
import argparse
import binascii
from PCA9685_CAMERAHEAD import moveCameraHead
from threading import Thread, Timer
from DRV8835_TWINGEAR import DRV8835TwinGear
# システムコマンド関連
import subprocess, re
import math
import os

ADDR_BSTICK = '30:ae:a4:0e:4f:12'

# キャラクタリスティックのハンドル値はgatttool使って調べられる。
# gatttool -b 30:ae:a4:0e:4f:12 -t randam -I
# connect
# primary  ・・・サービスのハンドルとUUIDの一覧がバーっとでる。
# char-desc <サービスのハンドル＞ ・・・キャラクタリスティックの〃
# [30:ae:a4:0e:4f:12][LE]> char-desc 0x0026
HANDLE_STICK_R = 0x002a
HANDLE_STICK_L = 0x002c
HANDLE_BUTTON1 = 0x0030
HANDLE_BUTTON2 = 0x0032
HANDLE_RSSI    = 0x0034

# DCモーター使用準備
Drv = DRV8835TwinGear()

#キャラクタリスティック値からサーボ角度への変換
# charactaristic は今回の環境の場合、おおよそ 0x000 〜 0xfff の値を取る。センターは0x700である。
# これを -90度 〜 +90度 となるよう変換する。
def c2tilt( chr ):
    maxtilt = 90.00
    #0xe00以上は0xe00とみなす。
    mchr = chr
    if mchr > 0xe00:
        mchr = 0xe00
    mchr = mchr - 0x700 # -0x61 〜 0x61 の範囲へ補正x
    tilt = ( mchr / 0x700 ) * maxtilt * -1
    return tilt

# -100 〜 100 となるよう変換する。
def c2duty( chr ):
    maxduty = 100
    #0xe00以上は0xe00とみなす。
    mchr = chr
    if mchr > 0xe00:
        mchr = 0xe00
    mchr = mchr - 0x700 # -0x61 〜 0x61 の範囲へ補正x
    duty = int(( mchr / 0x700 ) * maxduty * -1 ) 
    return duty

# Peripheralへコネクトするためのクラス（Peripheralクラスを継承）
# インスタンスを生成した時点でコネクトしてくれる。
class Connection(Peripheral, Thread):
    def __init__(self, dev):
        Peripheral.__init__(self, dev.addr, addrType="public")
        Thread.__init__(self)
        self.setDaemon(True)

# Notify受信したときのハンドラー
class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.button1_counter = 0
        
    def handleNotification(self, cHandle, data):
        c_data = binascii.b2a_hex(data)
        datah = int(c_data, 16)
        if cHandle == HANDLE_STICK_R:
            stick1_lr = (datah & 0xffff0000) >> 0x10
            stick1_ud = (datah & 0x0000ffff)
            moveCameraHead(c2tilt(stick1_lr), c2tilt(stick1_ud))
        if cHandle == HANDLE_STICK_L:
            stick2_lr = (datah & 0xffff0000) >> 0x10
            stick2_ud = (datah & 0x0000ffff)
            Drv.MoveTwinGear(c2duty(stick2_lr), c2duty(stick2_ud))
        if cHandle == HANDLE_BUTTON1:
            button1 = (datah & 0xff000000) >> 0x18
        if cHandle == HANDLE_BUTTON2:
            button2 = (datah & 0xff000000) >> 0x18

def main():
    while True:
        scanner = Scanner() # スキャン開始。
        print( 'scan start.')
        while True:
            devices = scanner.scan(5.0)
            for device in devices:
                if device.addr != ADDR_BSTICK:
                    continue
                con = Connection( device )
                con.setDelegate(NotifyDelegate())
                con.start()
                print( "connect to:",device.addr," RSSI=",device.rssi)
                con.writeCharacteristic(HANDLE_RSSI, 
                        str(device.rssi).encode('utf-8'), 0)
                while True:
                    try:
                        if con.waitForNotifications(10):
                            continue
                        print("wait..")
                    except BTLEException:
                        print("BTLEException. Now retry..")
                        pass
                    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    GPIO.cleanup()
