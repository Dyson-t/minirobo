# DRV8835モータードライバから２つのDCモーターを同時制御するクラス

import RPi.GPIO as GPIO
from time import sleep
import math

P_AIN1 = 20
P_AIN2 = 21
P_BIN1 = 19
P_BIN2 = 26

class DRV8835TwinGear:
   
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([P_AIN1,P_AIN2,P_BIN1,P_BIN2], GPIO.OUT)
        self.pwm_a1 = GPIO.PWM(P_AIN1, 50)
        self.pwm_a2 = GPIO.PWM(P_AIN2, 50)
        self.pwm_b1 = GPIO.PWM(P_BIN1, 50)
        self.pwm_b2 = GPIO.PWM(P_BIN2, 50)
        self.pwm_a1.start(0)
        self.pwm_a2.start(0)
        self.pwm_b1.start(0)
        self.pwm_b2.start(0)

    def ChangeDuty(self, lfb, lduty, rfb, rduty): # 前進(0)・後退(1)、Duty比
        if lfb == 0: #左前進
            self.pwm_b1.ChangeDutyCycle(0)
            self.pwm_b2.ChangeDutyCycle(lduty)
        else: #左後退
            self.pwm_b1.ChangeDutyCycle(lduty)
            self.pwm_b2.ChangeDutyCycle(0)
        
        if rfb == 0:
            self.pwm_a1.ChangeDutyCycle(0)
            self.pwm_a2.ChangeDutyCycle(rduty)
        else:
            self.pwm_a1.ChangeDutyCycle(rduty)
            self.pwm_a2.ChangeDutyCycle(0)

    # ジョイスティック値はそれぞれ最大 L:100 R:-100、U：100 D:-100 の値を取る。
    # これを左右のモーターの正転・逆転 及びDUTY比へ変換する。
    def MoveTwinGear(self, ratio_lr, ratio_ud):
        #仮実装。なぜか左右逆にまがってしまうので。。。
        ratio_lr = ratio_lr * -1
        #スティックの角度
        #スティック真右が0度。真左が180度。真上が90度。真下が-90度とする。
        radian = math.atan2(ratio_ud, ratio_lr)
        degree = math.degrees(radian)
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
        self.ChangeDuty(lfb, lduty, rfb, rduty)


# test code
if __name__ == '__main__':
    try:
        drv = DRV8835TwinGear()
        while True:
            drv.ChangeDuty(1, 100, 0, 50)

    except KeyboardInterrupt:
        pass

    GPIO.cleanup()
