import time
from functools import wraps
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from gui.base import BaseMessageBox
from gui.param_ui import ParamDialog
from gui.progress_ui import ProgressDialog
from backend import system
from backend.settings import settings

from algorithm.gaps.size_detector import SizeDetector


def help_handler():
    QMessageBox.information(BaseMessageBox(), "如何使用？", "鼠标左键按住拼图拖拉\n按住鼠标中键调整视角\n鼠标右键移出拼图\n按住Ctrl键缩放更快")


def about_handler():
    QMessageBox.information(BaseMessageBox(), "关于此软件", "版本：1.0.1 beta\n作者：JamesHoi@天璇Merak\n最后更新：2021.01.23")


def check_project_is_open(func):
    @wraps(func)
    def wrapper(self):
        if not settings.is_open:
            QMessageBox.information(BaseMessageBox(), "错误", "请先打开或新建项目")
            return None
        return func(self)

    return wrapper


def warn_all_replace(func):
    @wraps(func)
    def wrapper(self):
        reply = QMessageBox.question(self, '注意', "运行脚本后不可逆，是否继续")
        if reply != QMessageBox.Yes: return
        return func(self)

    return wrapper


# 获得含有透明度的QPixmap
# param  filePath:图片路径 opacity:透明度(0~255,越小越透明)
# return pMap:QPixmap对象
def getOpacityPixmap(file_path, opacity):
    p_map = QPixmap(file_path)  # 获取图片
    temp = QPixmap(p_map.size())
    temp.fill(Qt.transparent)
    p = QPainter(temp)
    p.setCompositionMode(QPainter.CompositionMode_Source)
    p.drawPixmap(0, 0, p_map)
    p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
    p.fillRect(temp.rect(), QColor(0, 0, 0, opacity))  # 根据QColor中第四个参数设置透明度，0～255
    p.end()
    return temp


def show_piece_info(piece_size, columns, rows, pieces_num):
    QMessageBox.information(BaseMessageBox(), "分割图片",
                            "图片碎片大小：{}像素\n"
                            "长碎片数量：{}\n"
                            "宽碎片数量：{}\n"
                            "共{}块碎片".format(piece_size, columns, rows, pieces_num))


def ask_open_pic_path(ask_text="请选择图片"):
    return QFileDialog.getOpenFileName(None, ask_text, system.get_desktop(),
                                       "图片文件 (*.jpg *.gif *.png *.jpeg)")[0]


def ask_save_pic_path():
    return QFileDialog.getSaveFileName(None, "选择保存位置",
                                       system.get_desktop() + "/puzzle.png",
                                       "图片文件 (*.jpg *.png *.jpeg)")[0]


def ask_path(ask_text):
    return QFileDialog.getExistingDirectory(None, ask_text, system.get_desktop())


def wrapper_with_ask_param(param_text, text_width, task_fun):
    param_ui = ParamDialog(param_text, text_width)
    param_ui.complete_signal.connect(task_fun)
    param_ui.exec_()


def try_size_detect(image):
    try:
        detector = SizeDetector(image)
        piece_size = detector.detect_piece_size()
        return piece_size
    except:
        QMessageBox.information(BaseMessageBox(), "错误", "无法自动识别拼图大小，请手动输入大小")
        return -1


def wrapper_with_init_size(img, task_fun):
    piece_size = try_size_detect(img)
    reply = QMessageBox.question(BaseMessageBox(), '提示', "检测到碎片大小为{}像素，是否正确？"
                                 .format(piece_size)) if piece_size != -1 else QMessageBox.No
    if reply == QMessageBox.Yes:
        task_fun([piece_size])
    else:
        wrapper_with_ask_param("输入碎片图片大小（单位：像素，例: 42）", 300, task_fun)


def wrapper_param_progress_fun(task_run, param_text, param_len, progress_len):
    '''
    :param task_run: 运行函数 ，必须格式为queue,params
    :param param_text:  询问输入参数文字
    :param progress_len:  进度条界面的宽度
    :param param_len:  参数界面的宽度
    :return:
    '''

    def task_fun(params):
        if len(params) is 0: return
        progress_ui = ProgressDialog(task_run, progress_len, params)
        progress_ui.exec_()

    wrapper_with_ask_param(param_text, param_len, task_fun)
