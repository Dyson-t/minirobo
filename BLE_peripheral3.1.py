# ESP32とコネクトし、ノーティファイを待ち続ける。
# ノーティファイされたデータに従い、カメラヘッド、DCモーター動かす。
# 
# ポイント
# □コネクト成功するまで自動リトライするようにしたい
# 　　仕掛け）Peripheralクラスを継承したBstickクラスにThreadクラスも他重軽傷し、
#           別スレッドからつながるまでコネクトし続けるようにした。このやり方は
#           ambientのgithubを参考にした。
# □ラズパイ側のボタンで起動できるようにした（起動のしかけは別コード）
# ■上の案ではなく、ラズパイ起動時に自動起動するようにする。
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
# □駆動系を別ソース化
# □lcd.printをprintと同じように使えるようにしたい。変数埋め込みとか
# □カメラヘッドの動きを滑らかにしたい。PWMの解像度UP
# □DCモーターのノイズでサーボが誤動作するのでコンデンサ追加したい（ハード側）

import RPi.GPIO as GPIO
from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import sys
import struct
from datetime import datetime
import argparse
import binascii
from PCA9685_test import setSurboAngle
from threading import Thread, Timer
from DRV8835_TWINGEAR import DRV8835TwinGear
# LCD関連
import lcd_lib
# システムコマンド関連
import subprocess, re
import math

ADDR_BSTICK = '30:ae:a4:0e:4f:12'

# キャラクタリスティックのハンドル値はgatttool使って調べられる。
# gatttool -b 30:ae:a4:0e:4f:12 -t randam -I
# connect
# primary  ・・・サービスのハンドルとUUIDの一覧がバーっとでる。
# char-desc <サービスのハンドル＞ ・・・キャラクタリスティックの〃
HANDLE_STICKS = 0x002a
HANDLE_BUTTON1 = 0x002e
HANDLE_BUTTON2 = 0x0030
HANDLE_RSSI = 0x0032

# DCモーター使用準備
Drv = DRV8835TwinGear()

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

# -100 〜 100 となるよう変換する。
def c2duty( chr ):
    maxduty = 100
    #0xc2以上は0xc2とみなす。
    mchr = chr
    if mchr > 0xc2:
        mchr = 0xc2
    mchr = mchr - 0x61 # -0x61 〜 0x61 の範囲へ補正x
    duty = int(( mchr / 0x61 ) * maxduty * -1 ) 
    return duty

# ジョイスティック値はそれぞれ最大 L:100 R:-100、U：100 D:-100 の値を取る。
# これを左右のモーターの正転・逆転 及びDUTY比へ変換する。
def moveTwinGear(ratio_lr, ratio_ud):
    #仮実装。なぜか左右逆にまがってしまうので。。。
    ratio_lr = ratio_lr * -1
    #スティックの角度
    #スティック真右が0度。真左が180度。真上が90度。真下が-90度とする。
    radian = math.atan2(ratio_ud, ratio_lr)
    degree = math.degrees(radian)
    print( "digree=", degree)
    # 真横に近い角度の場合は超信地旋回する。
    if (10 >= degree and degree >= -10) or (degree >= 170) or ( degree <= -170): 
        if ratio_lr >= 0:
            lfb = 1
            rfb = 0
            lduty = ratio_lr
            rduty = ratio_lr
        else:
            lfb = 0
            rfb = 1
            lduty = ratio_lr * -1
            rduty = ratio_lr * -1
    else:
        lduty = ratio_ud
        rduty = ratio_ud
        # LR方向の傾き（X）、UD(Y）として、三平方の定理より中心からの距離を求める。
        distance = int(math.sqrt(pow(ratio_ud,2) + pow(ratio_lr,2)))
        # LRの比率を求める
        lengthL = 100 + ( ratio_lr * -1 )
        lengthR = 100 - ( ratio_lr * -1 )
        ratio = lengthL / (lengthL + lengthR)
        # 距離に応じてratioがきつめに出るので補正する。
        # 中心からの距離が100以上の場合は100とみなす。
        if distance >= 100:
            ratio = ratio * (100 / distance)
            distance = 100
        # LR方向の値で補正
        if ratio_lr <= -5: # 右に倒してる場合
            # 右モーターにratioを掛ける。
            rduty = int(( 1 - ratio ) * distance)
            # 左モーターは距離をそのまま適用
            lduty = distance
        elif ratio_lr >= 5: # 左に倒している場合
            # 右モーターは距離をそのまま適用
            rduty = distance
            # 左モーターにratioを掛ける。
            lduty = int( ratio * distance)
        else:
            rduty = distance
            lduty = distance
        # 正転・逆転を求める。
        if degree >= 0: # 前進
            lfb = 0 # 0:正転・1:逆転
            rfb = 0
        else: # 後退
            lfb = 1 # 0:正転・1:逆転
            rfb = 1
    #print(ratio_lr, ratio_ud, " -> ", lfb, lduty, rfb, rduty)
    Drv.ChangeDuty(lfb, lduty, rfb, rduty)

# Bstick へコネクトするためのクラス（Peripheralクラスを継承）
# インスタンスを生成した時点でコネクトしてくれる。
class Bstick(Peripheral, Thread):
    def __init__(self, dev):
        Peripheral.__init__(self, dev.addr, addrType="public")
        Thread.__init__(self)
        self.setDaemon(True)

# Notify受信したときのハンドラー
class NotifyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        
    def handleNotification(self, cHandle, data):
        c_data = binascii.b2a_hex(data)
        print( "Notify handler called.cHandle=",cHandle," data=", c_data)
        #c_handle = binascii.b2a_hex(cHandle)
        if cHandle == HANDLE_STICKS:
            datah = int(c_data, 16)
            stick1_lr = (datah & 0xff000000) >> 0x18
            stick1_ud = (datah & 0x00ff0000) >> 0x10
            moveCameraHead(c2tilt(stick1_lr), c2tilt(stick1_ud))
            stick2_lr = (datah & 0x0000ff00) >> 0x08
            stick2_ud = (datah & 0x000000ff)
            moveTwinGear(c2duty(stick2_lr), c2duty(stick2_ud))
            
        if cHandle == HANDLE_BUTTON1:
            # dataには別のキャラクタリスティックの値が残ってる（バグ？）ので、
            # 必要な部分だけ取得。例えば（0x01006161 )と入っている。
            datah = int(c_data, 16)
            button1 = (datah & 0xff000000) >> 0x18
            if button1 == 1:
                lcd.print("shoooot!!")
        if cHandle == HANDLE_BUTTON2:
            datah = int(c_data, 16)
            button2 = (datah & 0xff000000) >> 0x18
            if button2 == 1:
                lcd.print("shoooot 2 !!")
            
scannedDevs = {}
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        print("discover:", dev.addr)
        if dev.addr == ADDR_BSTICK:
            if dev.addr in scannedDevs.keys():
                return
            print("connection start") 
            devThread = Bstick(dev)
            devThread.setDelegate(NotifyDelegate())
            scannedDevs[dev.addr] = devThread
            devThread.start()
            print("connect:", dev.addr, 'RSSI=', dev.rssi)
            lcd.print(dev.addr)
            devThread.writeCharacteristic(HANDLE_RSSI, str(dev.rssi).encode('utf-8'), 0)
            while True: # Notify待ち
                if devThread.waitForNotifications(300.0):
                    continue
                print("wait..")

try:
    # LCDオブジェクト生成
    lcd = lcd_lib.LCD(fontsize=8, fontpath='/home/pi/font/misakifont/misaki_gothic.ttf')

    # Scannerインスタンスを生成するとスキャン開始
    # withDelegateでデバイス見つけたときのハンドラーを渡しておくと呼んでくれる。
    while True:
        scanner = Scanner().withDelegate(ScanDelegate())
        lcd.print( 'scan start.')
        try:
            while True:
                scanner.scan(5.0)
        except BTLEException:
            scannedDevs = {}
            lcd.print( 'BTLE Exception.')
            pass

except KeyboardInterrupt:
    pass

GPIO.cleanup()
