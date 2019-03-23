# テスト１
# DCモーター一つだけつないで、PWMありで動くか確認

import RPi.GPIO as GPIO
from time import sleep

P_AIN1 = 20
P_AIN2 = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup([P_AIN1,P_AIN2], GPIO.OUT)

pwm_a1 = GPIO.PWM(P_AIN1, 50)
pwm_a2 = GPIO.PWM(P_AIN2, 50)
pwm_a1.start(100)
pwm_a2.start(100)

try:
    while True:
        pwm_a1.start(10)
        pwm_a2.start(0)
        print('10')
        sleep(2)
        pwm_a1.start(20)
        pwm_a2.start(0)
        print('20')
        sleep(2)
        pwm_a1.start(30)
        pwm_a2.start(0)
        print('30')
        sleep(2)
        pwm_a1.start(40)
        pwm_a2.start(0)
        print('40')
        sleep(2)
        pwm_a1.start(50)
        pwm_a2.start(0)
        print('50')
        sleep(2)
        pwm_a1.start(75)
        pwm_a2.start(0)
        print('75')
        sleep(2)
        pwm_a1.start(100)
        pwm_a2.start(0)
        print('100')
        sleep(2)
except KeyboardInterrupt:
    pass

GPIO.cleanup()
