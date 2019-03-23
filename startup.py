# ミニロボ起動処理
# systemdにて自動起動する想定

from time import sleep
# LCD関連
import lcd_lib
# システムコマンド関連
import subprocess, re
import minirobo 

# LCDオブジェクト生成
lcd = lcd_lib.LCD(fontsize=8, fontpath='/home/pi/font/misakifont/misaki_gothic.ttf')

#IPアドレスが取得できるまで調べ続ける
ip_ok = 0
while ip_ok == 0:
    try:
        lcd.print("IPを取得しています")
        r = subprocess.check_output("ip addr | grep 192", shell=True)
        s = r.decode( "utf-8")
        ip_list = re.findall(r'(192\.\d+\.\d+\.\d+)\/', s)
        print(ip_list)
        if len( ip_list ) != 0: 
            ip_ok = 1
        sleep(0.5)
    except:
        pass

ip_list = ["IP address:OK"] + ip_list
print(ip_list)

for str in ip_list:
    lcd.print(str)

lcd.print( 'Robo initializing..')
#sleep(30)
minirobo.main()
# mjpeg-streamer起動
r = 1
while r != 0:
    try:
        r = subprocess.check_output("sh /home/pi/lib/mjpg-streamer/start.sh", shell=True)
        #cd.print( 'mjpeg-streamer started' )
        lcd.print( 'http://' + ip_list[1] + ':9000/?action=stream')
    except:
        lcd.print( 'mjpeg-streamer start failed.' )

# blynk起動
# try:
#     r = subprocess.check_output("sudo /home/pi/lib/blynk/blynk --token 201945455ed74b30995bf4d8d2e43cfd", shell=True)
#     lcd.print( 'blynk started' )
#     print(r)
# except:
#     lcd.print( 'blynk start failed.' )


lcd.print('ready')
