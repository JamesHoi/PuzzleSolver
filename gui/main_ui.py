import sys

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDockWidget

from gui.puzzle_list import PuzzleListWidget
from gui.view_ui import ViewWidget
from gui.base import BaseMainWindow, BaseMessageBox
from gui.common import *
from gui.param_ui import ParamDialog
from gui.progress_ui import ProgressDialog
from backend.settings import settings
from backend import system

'''all import for gaps'''
import cv2
import numpy as np
from algorithm.gaps import image_helpers
from algorithm.gaps.size_detector import SizeDetector
from algorithm.gaps.genetic_algorithm import GeneticAlgorithm
from algorithm.brute import brute_task
from algorithm.common import cv_img2pil, pil_img2cv, save_cv_img, save_combine_cv_img,save_cv_pieces,cv_imread,cv_imwrite


class MainWindow(BaseMainWindow):
    def __init__(self):
        # 初始化UI
        super().__init__()

        # 子窗口
        self.dock_widget = QDockWidget()
        self.dock_widget.setWindowTitle("未拼接的拼图")
        self.puzzle_list_widget = None
        self.view_ui = None

        # slot连接
        self.action_new.triggered.connect(self.new_handler)
        self.action_add.triggered.connect(self.add_background_handler)
        self.action_open.triggered.connect(self.open_handler)
        self.action_fullscreen.triggered.connect(self.window_handler)
        self.action_opacity.triggered.connect(self.opacity_handler)
        self.action_reset_scale.triggered.connect(self.reset_scale)
        self.action_puzzle_window.triggered.connect(self.open_list)
        self.action_exit.triggered.connect(self.exit)
        self.action_help.triggered.connect(help_handler)
        self.action_about.triggered.connect(about_handler)
        self.action_gaps.triggered.connect(self.gaps_handler)
        self.action_del_brush.triggered.connect(self.del_brush_handler)
        self.action_compare.triggered.connect(self.compare_handler)
        self.action_combine.triggered.connect(self.combine_handler)
        self.action_separate.triggered.connect(self.separate_handler)
        self.action_export_puzzle.triggered.connect(self.export_puzzle_handler)
        self.action_export_img.triggered.connect(self.export_img_handler)
        self.action_line_color.triggered.connect(self.line_color_handler)
        self.action_del_bg.triggered.connect(self.del_bg_handler)
        self.action_shuffle.triggered.connect(self.shuffle_handler)
        self.action_reset_puzzle.triggered.connect(self.reset_puzzle_handler)

    def init_sub_widget(self):
        # 拼图碎片列表ui
        self.puzzle_list_widget = PuzzleListWidget()
        self.dock_widget.setWidget(self.puzzle_list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
        # 拼图主视窗
        self.view_ui = ViewWidget()
        self.setCentralWidget(self.view_ui)
        self.view_ui.setFocus()

    @check_project_is_open
    def del_bg_handler(self):
        settings.bg_img = None
        settings.bg_img_cv2 = None

    def window_handler(self):
        full_screen = self.action_fullscreen.text() == "全屏"
        if full_screen:
            self.showFullScreen()
        else:
            self.showNormal()
        self.action_fullscreen.setText(("退出" if full_screen else "") + "全屏")

    @check_project_is_open
    def export_img_handler(self):
        save_dir = ask_save_pic_path()
        if save_dir == "": return
        # TODO: 没有的填充白色
        
        pieces = [settings.pieces[i] for i in settings.pieces_index_list]
        save_combine_cv_img(pieces, settings.pic_rows, settings.pic_columns,save_dir)

    @check_project_is_open
    def export_puzzle_handler(self):
        save_dir = ask_path("选择保存路径")
        if save_dir == "": return
        for i in range(settings.pieces_num):
            save_cv_img(settings.pieces[i],save_dir + "/{}.png".format(i))

    def change_opacity(self, data_list):
        if len(data_list) is not 0:
            settings.opacity = int(data_list[0])
            settings.bg_img = getOpacityPixmap(settings.bg_img_dir, settings.opacity)

    @check_project_is_open
    def opacity_handler(self):
        wrapper_with_ask_param("输入参数 图片透明度0-255",200,self.change_opacity)

    @check_project_is_open
    def line_color_handler(self):
        def task_fun(params):
            settings.grid_color = [int(p) for p in params[0].split(',')]
        wrapper_with_ask_param("输入网格线颜色(RGB顺序)(范例: 0,255,0)", 300,task_fun)

    @check_project_is_open
    def reset_scale(self):
        self.view_ui.scale_reset_signal.emit()

    def new_handler(self):
        directory, img_type = QFileDialog.getOpenFileName(self, '请选择碎片图片', system.get_desktop(),
                                                          "图片文件 (*.jpg *.gif *.png *.jpeg)")
        if directory == "": return
        image = cv_imread(directory)

        def task_fun(params):
            if len(params) is 0: return
            piece_size = int(params[0])
            settings.pieces, rows, columns = image_helpers.flatten_image(image, piece_size)
            show_piece_info(piece_size, columns, rows, len(settings.pieces))
            settings.pic_rows, settings.pic_columns = rows, columns
            settings.src_img = image
            settings.pic_height, settings.pic_width, _ = image.shape
            settings.piece_size = piece_size
            settings.pieces_num = len(settings.pieces)
            settings.is_open = True
            self.init_sub_widget()
        wrapper_with_init_size(image,task_fun)

    def open_handler(self):
        # dump binary
        settings.is_open = True

    @check_project_is_open
    def add_background_handler(self):
        directory = ask_open_pic_path("请选择背景图片")
        if directory == "": return
        temp_img = getOpacityPixmap(directory, settings.opacity)
        right = temp_img.height() == settings.pic_height and temp_img.width() == settings.pic_width
        if not right:
            QMessageBox.information(BaseMessageBox(), "注意", "检测到背景图片和原图分辨率不一致，将强制伸缩背景图片！")
            temp_img.scaled(self.pic_width, self.pic_height, Qt.IgnoreAspectRatio)
        settings.bg_img_dir = directory
        settings.bg_img = temp_img
        settings.bg_img_cv2 = cv_imread(directory)

    @check_project_is_open
    def reset_puzzle_handler(self):
        pass

    @check_project_is_open
    def del_brush_handler(self):
        def task_run(queue, params):
            brush_color = tuple(map(int, params[0].split(',')))
            bg_color = tuple(map(int, params[1].split(',')))
            piece_num = len(settings.pieces)
            for img_index in range(piece_num):
                img = cv_img2pil(settings.pieces[img_index])
                WIDTH = img.size[0]
                HEIGHT = img.size[0]
                for i in range(HEIGHT):
                    for j in range(WIDTH):
                        if img.getpixel((j, i)) != brush_color:
                            img.putpixel((j, i), bg_color)
                settings.pieces[img_index] = pil_img2cv(img)
                queue.put(
                    ((img_index / piece_num) * 100, "正在操作{}/{}".format(img_index, piece_num), "正在删除非画笔颜色外的颜色", False))
            settings.refresh_puzzle_board = True
            settings.refresh_puzzle_list = True
            queue.put((100, "操作完成", "正在删除非画笔颜色外的颜色", True))

        param_text = "输入画笔颜色和背景颜色(RGB顺序)(范例: 0,0,0;255,255,255)"
        wrapper_param_progress_fun(task_run, param_text, 430, 250)

    def combine_handler(self):
        settings.read_dir = ask_path("选择含有图片的文件夹")
        if settings.read_dir == "": return
        settings.save_dir = ask_save_pic_path()
        if settings.save_dir == "": return

        def task_run(queue, params):
            [head, end] = [int(tmp) for tmp in params[0].split("-")]
            columns, rows = int(params[1]), int(params[2])
            suffix = params[3]
            queue.put((50, "初始化完成", "正在拼接图片", False))
            pieces = [cv_imread(settings.read_dir + "/" + str(i) + suffix) for i in range(head, end + 1)]
            save_combine_cv_img(pieces, rows, columns, settings.save_dir)
            queue.put((100, "拼接完成", "正在拼接图片", True))

        param_text = "输入图片序号，长碎片数量，宽碎片数量，以及后缀名(范例1-100;44;25;.png)"
        wrapper_param_progress_fun(task_run, param_text, 540, 250)

    def separate_handler(self,combine=False):
        settings.read_dir = ask_open_pic_path()
        if settings.read_dir == "": return
        if combine: settings.save_dir = ask_save_pic_path()
        else: settings.save_dir = ask_path("选择保存的路径")
        if settings.save_dir == "": return

        reply = QMessageBox.question(self, '提示', "是否随机打乱顺序") if not combine else QMessageBox.Yes
        settings.is_shuffle = reply == QMessageBox.Yes
        image = cv_imread(settings.read_dir)

        def task_fun(params):
            piece_size = int(params[0])
            pieces, rows, columns = image_helpers.flatten_image(image, piece_size)

            if settings.is_shuffle: np.random.shuffle(pieces)
            if combine: save_combine_cv_img(pieces,rows,columns,settings.save_dir)
            else: save_cv_pieces(pieces,settings.save_dir)

        wrapper_with_init_size(image,task_fun)

    def shuffle_handler(self):
        self.separate_handler(combine=True)

    @check_project_is_open
    @warn_all_replace
    def gaps_handler(self):
        settings.edit_img = image_helpers.assemble_image(settings.pieces, settings.pic_rows, settings.pic_columns)

        def gaps_run(queue, params):
            population, generations = int(params[0]), int(params[1])
            algorithm = GeneticAlgorithm(settings.edit_img, settings.piece_size, population, generations)
            solution = algorithm.start_evolution(verbose=False, queue=queue)

            settings.pieces = [piece.image for piece in solution.pieces]
            settings.pieces_index_list_not_placed.clear()
            num = settings.pieces_num; size = settings.piece_size
            rows = settings.pic_rows; columns = settings.pic_columns
            for i in range(num):
                settings.pieces_index_list.append(i)
                settings.pieces_rect_list.append(QRect((i % columns) * size, int(i / columns) * size, size, size))
            settings.refresh_puzzle_list = True
            queue.put((100, "完成", "正在尝试用gaps拼图", True))

        wrapper_param_progress_fun(gaps_run, "输入参数 population; generations", 260, 250)
        self.reset_scale()  # 刷新一下

    @check_project_is_open
    @warn_all_replace
    def compare_handler(self):
        def task_run(queue, params):
            settings.pieces_index_list_not_placed.clear()
            threshold = int(params[0])
            pieces, rows, columns = image_helpers.flatten_image(settings.bg_img_cv2, settings.piece_size)
            num = settings.pieces_num
            size = settings.piece_size

            origin_pieces = [cv_img2pil(pieces[i]) for i in range(num)]
            modified_pieces = [cv_img2pil(settings.pieces[i]) for i in range(num)]
            index_list = brute_task(queue, threshold, modified_pieces, origin_pieces)
            # 获取成功拼接的图片索引
            for i in range(num):
                if index_list[i] == -1: continue
                settings.pieces_index_list.append(index_list[i])
                settings.pieces_rect_list.append(QRect((i % columns) * size, int(i / columns) * size, size, size))
            # 获取没成功拼接的图片索引
            for i in range(num):
                try:
                    _ = settings.pieces_index_list.index(i)
                except ValueError:
                    settings.pieces_index_list_not_placed.append(i)
            queue.put((100, "完成", "正在尝试暴力对比像素点拼图", True))

        if settings.bg_img is None:
            QMessageBox.information(BaseMessageBox(), "错误", "请先导入原图")
            return
        wrapper_param_progress_fun(task_run, "相似度阈值(大约10-60, 数值越小越信任原图)", 320, 250)
        self.reset_scale()  # 刷新一下

    @check_project_is_open
    def open_list(self):
        self.dock_widget.show()

    def exit(self):
        reply = QMessageBox.question(self, '注意', "关闭软件所有未导出的数据\n将会删除，确定退出吗？(注意是导出！)")
        if reply == QMessageBox.Yes:
            sys.exit(0)

    def closeEvent(self, event):
        self.exit()
