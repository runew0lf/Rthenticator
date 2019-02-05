import json
import re
import sys
import time
from urllib.parse import parse_qs, unquote, urlsplit

import pyotp
import pyperclip
from PIL import Image
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFileDialog, QFrame,
                             QLabel, QListWidget, QMainWindow, QProgressBar,
                             QPushButton, QMenu, QStyle, QSystemTrayIcon, qApp, QAction)
from pyzbar.pyzbar import decode

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
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon.ico'))
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.systemIcon)
        self.tray_icon.show()

        # Button Setup
        self.btnImport = QPushButton("Import", self)
        self.btnImport.move(50, 320)
        self.btnImport.setStyleSheet("background-color: #737C7D; color: #E9E6E4")
        self.btnImport.clicked.connect(self.btnImportClicked)

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
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.Listbox.setFocus(True)
        self.listboxClicked()
        self.show()

    # Restore view when tray icon doubleclicked
    def systemIcon(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.copy_auth_code()

    # Override closeEvent, to intercept the window closing event
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )

    def copy_auth_code(self):
        answer = self.Listbox.currentItem().text()
        totp = pyotp.TOTP(secrets[answer][0])
        self.label.setText(str(totp.now()))
        pyperclip.copy(totp.now())

    def progressTimer(self):
        current_time = int(time.time() % 30)
        self.progress.setValue(current_time)
        if current_time == 0:
            if self.isVisible():
                self.copy_auth_code()

    def listboxClicked(self):
        self.copy_auth_code()

    def btnImportClicked(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "QFileDialog.getOpenFileName()", "", "All Files (*)")
        if fileName:
            test = unquote(decode(Image.open(fileName))[0].data.decode("utf-8"))
            query = urlsplit(test).query
            params = parse_qs(query)
            start = "/totp/"
            end = "\\?"
            test = re.search(f'{start}(.*){end}', test).group(1)
            secrets[test] = [params['secret'][0]]
            self.Listbox.addItem(test)
            with open('secrets.json', 'w') as fh:
                json.dump(secrets, fh, sort_keys=True, indent=4)


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
