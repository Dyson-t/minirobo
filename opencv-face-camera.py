import cv2
from datetime import datetime
from time import sleep

# 顔認識用のファイル --- (*1)
CASCADE_DIR = "/usr/local/share/OpenCV/haarcascades/"
CASCADE_FILE = CASCADE_DIR + "haarcascade_frontalface_alt.xml"

# あまり小さなサイズは顔と認識しないように --- (*2)
MIN_SIZE = (150,150) 

# 顔認識用の分類器を生成 --- (*3)
cascade = cv2.CascadeClassifier(CASCADE_FILE)

# カメラをオープン --- (*4)
camera = cv2.VideoCapture(0)

# 繰り返し画像を判定する
try:
    while True:
        # カメラから画像を入力 --- (*5)
        _, img = camera.read()
        # グレイスケールに変換 --- (*6)
        igray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 顔認識 --- (*7)
        faces = cascade.detectMultiScale(igray, minSize=MIN_SIZE)
        if len(faces) == 0:
            continue # 顔がなかった場合
        # 認識した部分に印を付ける --- (*8)
        for (x,y,w,h) in faces:
            color = (255, 0, 0)
            cv2.rectangle(img, (x,y), (x+w, y+h),
                color, thickness=8) 
        # 画像を保存 --- (*9)
        s = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        fname = "face" + s + ".jpg"
        cv2.imwrite(fname, img)
        print("顔を認識しました")
        sleep(3) # 連続で認識しないように待機
    
except KeyboardInterrupt:
    print("ok.")


