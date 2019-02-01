import json
import sys
import time
import pyotp
import pyperclip
import re
from pyzbar.pyzbar import decode
from PIL import Image
from urllib.parse import unquote, urlsplit, parse_qs

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFrame, QLabel,
                             QListWidget, QMainWindow, QProgressBar,
                             QPushButton)

with open("secrets.json", "r") as fh:
    secrets = json.load(fh)


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        # Set size and centre window
        self.setGeometry(50, 50, 500, 400)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)

        self.move(qtRectangle.topLeft())

        self.setWindowTitle("Rthenticator")
        self.setWindowIcon(QIcon('icon.ico'))
        self.setStyleSheet("background-color: #2F3031")

        self.home()

    def home(self):
        # Button Setup
        self.btnPipBoy = QPushButton("Set PipBoy Color", self)
        self.btnPipBoy.move(50, 320)
        self.btnPipBoy.setStyleSheet("background-color: #737C7D; color: #E9E6E4")
        self.btnPipBoy.clicked.connect(self.btnPipBoyClicked)

        # Listbox Setup
        self.Listbox = QListWidget(self)
        self.Listbox.setAlternatingRowColors(True)
        self.Listbox.setFixedSize(220, 300)
        self.Listbox.move(10, 10)
        self.Listbox.setStyleSheet("alternate-background-color: #3F4041; color: #E9E6E4;")
        self.Listbox.itemClicked.connect(self.listboxClicked)
        for key in sorted(secrets):
            self.Listbox.addItem(key)
        self.Listbox.setCurrentRow(0)
        self.Listbox.currentItem().setSelected(True)

        # Frame Setup
        self.Frame = QFrame(self)
        self.Frame.setFixedSize(220, 300)
        self.Frame.move(266, 10)
        self.Frame.setFrameShape(QFrame.Shape.Panel)
        self.Frame.setFrameShadow(QFrame.Shadow.Plain)
        self.Frame.setStyleSheet("color: #828790")

        # Progress Bar Setup
        self.progress = QProgressBar(self)
        self.progress.setGeometry(266, 325, 200, 20)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("QProgressBar::chunk { background: #6187CB; }")
        self.progress.setRange(1, 29)

        # Progress Bar Timer Setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.progressTimer)
        self.timer.start(1000)

        # Label Setup
        self.label = QLabel(self)
        self.label.setGeometry(310, 220, 150, 40)
        self.label.setText("")
        self.label.setFont(QFont("Arial", 30, QFont.Bold))
        self.label.setStyleSheet("color: #E9E6E4")

        self.Listbox.setFocus(True)
        self.show()

    def progressTimer(self):
        current_time = int(time.time() % 30)
        self.progress.setValue(current_time)
        if current_time == 0:
            answer = self.Listbox.currentItem().text()
            totp = pyotp.TOTP(secrets[answer][0])
            self.label.setText(str(totp.now()))
            pyperclip.copy(totp.now())

    def listboxClicked(self):
        answer = self.Listbox.currentItem().text()
        totp = pyotp.TOTP(secrets[answer][0])
        self.label.setText(str(totp.now()))
        pyperclip.copy(totp.now())

    def btnPipBoyClicked(self):
        test = unquote(decode(Image.open('test.png'))[0].data.decode("utf-8"))
        query = urlsplit(test).query
        params = parse_qs(query)
        start = "/totp/"
        end = "\?"
        test = re.search(f'{start}(.*){end}', test).group(1)
        print(test)
        print(params['secret'][0])


def run():
    app = QApplication(sys.argv)
    GUI = Window()
    GUI.setVisible(True)
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass


if __name__ == "__main__":
    run()