import sys
import os
import cv2
import numpy as np
import time

from PyQt5.QtWidgets import QMainWindow, QWidget, QDialog, QAction
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.uic import loadUi

UI_Mapping = {
    # Widget
    "MainWindow": "gui/ui/main.ui",
    # Dialog
    "ParamDialog": "gui/ui/param.ui",
    "ProgressDialog": "gui/ui/progress.ui"
}


def program_dir():
    return sys._MEIPASS + "/" if hasattr(sys, 'frozen') else os.getcwd() + "/"


class Base():
    def __init__(self):
        super(Base, self).__init__()
        self._load_ui_file(self)

        # 设置图标
        self.icon = QIcon()
        self.icon.addPixmap(QPixmap(program_dir() + "gui/ui/icon.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(self.icon)

    @classmethod
    def _load_ui_file(cls, parent):
        loadUi(program_dir() + UI_Mapping[cls.__name__], parent)


class BaseMainWindow(Base, QMainWindow):
    pass


class BaseWidget(Base, QWidget):
    pass


class BaseMessageBox(QWidget):
    def __init__(self):
        super().__init__()
        self.icon = QIcon()
        self.icon.addPixmap(QPixmap(program_dir() + "Resource/icon.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(self.icon)


class BaseDialog(Base, QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint)


class Action(QAction):
    def __init__(self, text, qobject, fn):
        super().__init__(text, qobject)
        self.triggered.connect(fn)


class BaseImage(QImage):
    def __init__(self, data, scale=1):
        tmp = cv2.resize(data.astype(np.uint8), (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        cvImage = cv2.cvtColor(tmp, cv2.COLOR_BGR2RGB)
        h, w, channel = cvImage.shape
        # 颜色是三通道的
        bytesPerline = channel * w
        super().__init__(cvImage.data,w, h, bytesPerline,
                         QImage.Format_RGB888)


class BasePixmap(QPixmap):
    def __init__(self, data, scale=1):
        tmp = cv2.resize(data.astype(np.uint8), (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        cvImage = cv2.cvtColor(tmp, cv2.COLOR_BGR2RGB)
        h, w, channel = cvImage.shape
        # 颜色是三通道的
        bytesPerline = channel * w
        image = QImage(cvImage.data,w, h, bytesPerline,
                         QImage.Format_RGB888)
        super().__init__(image)


class UpdateThread(QThread):
    refresh_signal = pyqtSignal()

    def __init__(self, p):
        super(UpdateThread, self).__init__()
        self.running = True
        self.p = p

    def run(self):
        while self.running:
            self.refresh_signal.emit()
            time.sleep(0.05)