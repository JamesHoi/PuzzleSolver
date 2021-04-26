import sys
from PyQt5.QtWidgets import QApplication,QMessageBox,QWidget

from gui.base import BaseMessageBox
from gui.main_ui import MainWindow
from backend import system
from backend.except_handler import ExceptHookHandler


class Core(ExceptHookHandler):
    # 界面
    login_window = None
    main_window = None
    paint_thread = None

    def run(self):
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        if system.proc_exist():
            QMessageBox.information(BaseMessageBox(),"错误","程序已在运行")
            sys.exit(0)
        self.main_window = MainWindow()
        self.main_window.show()
        sys.exit(app.exec_())


instance = Core()
