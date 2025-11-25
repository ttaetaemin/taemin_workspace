import sys
import socket
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import QRegularExpression, QTimer
from struct import Struct

from_class = uic.loadUiType("TCP_Client.ui")[0]


class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.connected = False
        self.timer = QTimer(self)
        self.timer.start(1000)

        # IP validator
        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QRegularExpression("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + "$")
        self.ipEdit.setValidator(QRegularExpressionValidator(ipRegex, self))
        self.portEdit.setValidator(QIntValidator())
        self.degree.setValidator(QIntValidator())

        self.setWindowTitle("TCP Client")

        # signals
        self.ConnectBtn.clicked.connect(self.connect)
        self.led21.clicked.connect(self.clickLED21)
        self.led22.clicked.connect(self.clickLED22)
        self.led23.clicked.connect(self.clickLED23)
        self.move.clicked.connect(self.clickMove)
        self.timer.timeout.connect(self.timeout)

    def __del__(self):
        try:
            self.sock.close()
        except:
            pass
        self.connected = False

    def connect(self):
        ip = self.ipEdit.text().strip()
        port = int(self.portEdit.text().strip())
        self.sock = socket.socket()
        self.sock.connect((ip, port))
        self.sock.settimeout(2.0)

        self.connected = True
        self.format = Struct("<ii")  # 리틀엔디언 고정

        print("Connected")

    def timeout(self):
        # 센서 폴링 예: pin 34 (원하면 비활성화해도 됨)
        self.updateLED(34, 0)

    def clickMove(self):
        degree = int(self.degree.text())
        self.updateServo(5, degree)

    def clickLED21(self):
        self.updateLED(21, self.led21.isChecked())

    def clickLED22(self):
        self.updateLED(22, self.led22.isChecked())

    def clickLED23(self):
        self.updateLED(23, self.led23.isChecked())

    # ---- 공용: 정확히 size 바이트 수신 ----
    def recv_exact(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    # LED 제어: (pin, status) 튜플 출력
    def updateLED(self, pin, status):
        if not self.connected:
            return
        data = self.format.pack(int(pin), int(bool(status)))
        self.sock.sendall(data)

        buf = self.recv_exact(self.format.size)
        if len(buf) != self.format.size:
            print("⚠️ 수신 크기 부족:", len(buf))
            return

        rev = self.format.unpack(buf)  # (pin, status)
        if rev[0] == 34:
            # 센서 수신이면 GUI에만 반영
            try:
                self.sensor.setText(str(rev[1]))
            except Exception:
                pass
        else:
            # LED는 (pin, status) 형태로 터미널에 출력
            print(f"({rev[0]}, {rev[1]})")

    # Servo 제어: 각도만 출력
    def updateServo(self, pin, degree):
        if not self.connected:
            return
        data = self.format.pack(int(pin), int(degree))
        self.sock.sendall(data)
        # 서버 에코를 받는다면 아래 주석을 해제해도 됨(필수 아님)
        # _ = self.recv_exact(self.format.size)
        print(int(degree))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec())
