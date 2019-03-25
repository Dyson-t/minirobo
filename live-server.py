from http.server import HTTPServer, BaseHTTPRequestHandler
import cv2
from PCA9685_CAMERAHEAD_CLASS import CameraHead 

# 顔認識用のファイル --- (*1)
CASCADE_DIR = "/usr/local/share/OpenCV/haarcascades/"
CASCADE_FILE = CASCADE_DIR + "haarcascade_frontalface_alt.xml"

# あまり小さなサイズは顔と認識しないように --- (*2)
MIN_SIZE = (100,100) 

# 顔認識用の分類器を生成 --- (*3)
cascade = cv2.CascadeClassifier(CASCADE_FILE)

# カメラのデバイスをオープン
camera = cv2.VideoCapture(0)

# 
camerahead = CameraHead()

# Webサーバーのハンドラを定義 --- (*1)
class liveHTTPServer_Handler(BaseHTTPRequestHandler):

    # アクセスがあったとき
    def do_GET(self):
        #print("path=",self.path)
        # 画像を送信する --- (*2)
        if self.path[0:7] == "/camera":
            # ヘッダ
            self.send_response(200)
            self.send_header('Cotent-Type', 'image/jpeg')
            self.end_headers()
            # フレームを送信
            #_, frame = camera.read()
            #img = cv2.resize(frame, (300,200))

            ####### 試しに追加
            # カメラから画像を入力 --- (*5)
            _, img = camera.read()
            #img = cv2.resize(img, (300,200))
            # グレイスケールに変換 --- (*6)
            igray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 顔認識 --- (*7)
            faces = cascade.detectMultiScale(igray, minSize=MIN_SIZE)
            if len(faces) != 0:
                #print("顔を認識しました")
                # 認識した部分に印を付ける --- (*8)
                for (x,y,w,h) in faces:
                    color = (255, 0, 0)
                    cv2.rectangle(img, (x,y), (x+w, y+h),
                        color, thickness=8)
                # 最初に認識した顔だけ以下を行う。
                x,y,w,h = faces[0]
                #print(x,",",y,",",w,",",h)
                # 顔の座標を求める
                face_x = x + (w/2)
                face_y = y + (h/2)
                # 中心軸からのズレを求める
                # スクリーンサイズは多分600x400
                # ということは中心は300x200
                # 座標のズレ
                zure_x = 300 - face_x
                zure_y = 200 - face_y
                cv2.putText(img, '('+str(zure_x)+','+str(zure_y)+')',
                        (x-5, y-5), cv2.FONT_HERSHEY_PLAIN, 2, (255,128,0),
                        2, cv2.LINE_AA)
                cv2.putText(img, 'Oh! Good Looking.',
                        (0, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,128,128),
                        3, cv2.LINE_AA)
                #moveCameraHead((zure_x)/7.5, (zure_y * -1)/7.5)
                camerahead.moveCameraHeadRel((zure_x)/30, (zure_y*-1)/30)


            ######## ここまで

            # JPEGにエンコード
            param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            _, encimg = cv2.imencode('.jpg', img, param)
            self.wfile.write(encimg)
        # HTMLを送信する --- (*3)
        elif self.path == "/":
            # ヘッダ
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # HTMLを出力 
            try:
                f = open('live2.html', 'r', encoding='utf-8')
                s = f.read()
            except:
                s = "file not found"
            self.wfile.write(s.encode('utf-8'))
        else:
            self.send_response(404)
            self.wfile.write("file not found".encode('utf-8'))
try:
    # Webサーバーを開始 --- (*4)
    addr = ('', 8081)
    httpd = HTTPServer(addr, liveHTTPServer_Handler)
    print('サーバーを開始', addr)
    httpd.serve_forever()

except KeyboardInterrupt:
    httpd.socket.close()


