# テスト3
# DCモーター２つつないで、PWMありで動くか確認

import RPi.GPIO as GPIO
from time import sleep

P_AIN1 = 20
P_AIN2 = 21
P_BIN1 = 19
P_BIN2 = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup([P_AIN1,P_AIN2,P_BIN1,P_BIN2], GPIO.OUT)

pwm_a1 = GPIO.PWM(P_AIN1, 50)
pwm_a2 = GPIO.PWM(P_AIN2, 50)
pwm_b1 = GPIO.PWM(P_BIN1, 50)
pwm_b2 = GPIO.PWM(P_BIN2, 50)
pwm_a1.start(100)
pwm_a2.start(100)
pwm_b1.start(100)
pwm_b2.start(100)

try:
    d = 10
    while True:
        if d >= 100:
            d = 0        
        pwm_a1.ChangeDutyCycle(d)
        pwm_a2.ChangeDutyCycle(1)
        pwm_b1.ChangeDutyCycle(d)
        pwm_b2.ChangeDutyCycle(0)
        print(d)
        d = d + 10
        sleep(3)
except KeyboardInterrupt:
    pass


#参考
# バック PWMなし
#        GPIO.output(P_AIN1, GPIO.HIGH)
#        GPIO.output(P_AIN2, GPIO.LOW)
# アクセル PWMなし
#        GPIO.output(P_AIN1, GPIO.LOW)
#        GPIO.output(P_AIN2, GPIO.HIGH)

GPIO.cleanup()
