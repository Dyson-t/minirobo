# テスト１
# DCモーター一つだけつないで、PWMなしで動くか確認

import RPi.GPIO as GPIO
from time import sleep

P_AIN1 = 20
P_AIN2 = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup([P_AIN1,P_AIN2], GPIO.OUT)

#pwm_r = GPIO.PWM(R_VREF, 50)
#pwm_r.start(100)
try:
    while True:
        GPIO.output(P_AIN1, GPIO.HIGH)
        GPIO.output(P_AIN2, GPIO.LOW)
        sleep(1)
        #stop
        GPIO.output(P_AIN1, GPIO.LOW)
        GPIO.output(P_AIN2, GPIO.LOW)
        sleep(1)
        GPIO.output(P_AIN1, GPIO.LOW)
        GPIO.output(P_AIN2, GPIO.HIGH)
        sleep(1)
except KeyboardInterrupt:
    pass

GPIO.cleanup()
