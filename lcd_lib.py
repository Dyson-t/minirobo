# LCD関連
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep 

class LCD:
    # AdafruitLCDにテキスト出力するためのクラス
    # 2018/7/23 togawa 超簡易版

    # Raspberry Pi pin configuration
    RST = 24

    #美咲フォントを使いたい場合はこちら。fontsize=8じゃないときれいに表示されない。
    # Misaki Font, awesome 8x8 pixel Japanese font, can be downloaded from the following URL.
    # $ wget http://www.geocities.jp/littlimi/arc/misaki/misaki_ttf_2015-04-10.zip
    FONT_PATH = '/home/pi/font/misakifont/misaki_gothic.ttf'
    #FONT_PATH = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'

    def __init__(self, i2caddress=0x3c, fontsize=8, fontpath=FONT_PATH):
        # set member
        self.fontsize = fontsize
        self.fontpath = fontpath
        self.textlist = []
        #disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=self.RST, i2c_address=i2caddress)
        # Initialize library.
        self.disp.begin()
        # Clear display.
        self.disp.clear()
        self.disp.display()
        self.font = ImageFont.truetype(self.fontpath, self.fontsize, encoding='unic')
 
    def print(self, str):
        # 表示可能幅より長い文字列を指定された場合は折り返す。
        # なお、表示可能幅は、（width / フォントサイズの半分 ）で計算する。多分。。。
        limit_width = int(self.disp.width / (self.fontsize / 2))
        mstr = [str[i:i+limit_width] for i in range(0, len(str), limit_width)]
        self.textlist.extend(mstr)
        # limit
        limit_row = int(self.disp.height / self.fontsize)
        if len(self.textlist) > limit_row:
            disptextlist = self.textlist[-limit_row:]
        else:
            disptextlist = self.textlist
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = self.disp.width
        height = self.disp.height
        image = Image.new('1', (width, height))
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        x=0
        y=0
        for str in disptextlist:
            draw.text((x,y), str, font=self.font, fill=255)
            y+=self.fontsize
        self.disp.clear()
        self.disp.image(image)
        self.disp.display()

    def clear(self):
        self.textlist = []
        self.disp.clear()
        self.disp.display()

    
# test code
if __name__ == '__main__':
    testlcd = LCD()
    testlcd.print("1234567890abcdefghijklmnopqrstuvwxyz")
    testlcd.print("test2")
    testlcd.print("test3")
    sleep(0.1)
    testlcd.print("test4")
    sleep(0.1)
    testlcd.print("test5")
    sleep(0.1)
    testlcd.print("test6")
    sleep(0.1)
    testlcd.print("test7")
    sleep(0.1)
    testlcd.print("test8")
    sleep(0.1)
    testlcd.print("test9")
    sleep(0.1)
    testlcd.print("test10")
    sleep(0.1)
    testlcd.print("test11")
    sleep(0.1)
    testlcd.print("test12")
    testlcd.print("1234567890abcdefghijklmnopqrstuvwxyz")
    sleep(1.1)
    testlcd.clear()
