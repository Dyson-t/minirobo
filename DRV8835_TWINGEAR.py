# DRV8835モータードライバから２つのDCモーターを同時制御するクラス

import RPi.GPIO as GPIO
from time import sleep

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


# test code
if __name__ == '__main__':
    try:
        drv = DRV8835TwinGear()
        while True:
            drv.ChangeDuty(1, 100, 0, 50)

    except KeyboardInterrupt:
        pass

    GPIO.cleanup()
