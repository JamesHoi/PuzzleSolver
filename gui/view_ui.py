from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                             QGraphicsItem)
from PyQt5.QtCore import (QPoint, QPointF, QLine, QLineF, QRect, QRectF,
                          QTime, qrand, Qt, pyqtSignal)
from PyQt5.QtGui import (QBrush, QPen, QColor, QRadialGradient,
                         QPainter, QPainterPath,
                         QPixmap, QImage, QPicture)
import math

from gui.board_ui import PuzzleBoard
from backend.settings import settings


class Piece(QGraphicsItem):

    def __init__(self, graphWidget):
        super(Piece, self).__init__()
        self.graph = graphWidget

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)

    def boundingRect(self):
        adjust = 2.0
        return QRectF(-10 - adjust, -10 - adjust,
                      53 + adjust, 53 + adjust)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 0))
        painter.setBrush(Qt.darkGray)
        painter.setOpacity(0.5)
        painter.drawEllipse(-7, -7, 20, 20)
        painter.drawLine(-7, -7, 20, 20)
        painter.setOpacity(0.2)
        painter.drawRect(QRectF(QPointF(-10, -10), QPointF(20, 20)))

        # gradient = QRadialGradient(-3, -3, 10)
        # gradient.setCenter(3, 3)
        # gradient.setFocalPoint(3, 3)
        # gradient.setColorAt(1, QColor(Qt.yellow).lighter(120))
        # gradient.setColorAt(0, QColor(Qt.darkYellow).lighter(120))
        # painter.setBrush(QBrush(gradient))
        # painter.setPen(QPen(Qt.black, 0))
        # painter.drawEllipse(-10, -10, 20, 20)

    def mousePressEvent(self, event):
        self.update()
        super(Piece, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super(Piece, self).mouseReleaseEvent(event)


class ViewWidget(QGraphicsView):
    scale_reset_signal = pyqtSignal()

    def __init__(self):
        super(ViewWidget, self).__init__()
        # 初始化scene
        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.scene.setSceneRect(-self.width() / 2, -self.height() / 2, self.width(), self.height())
        self.setScene(self.scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # 拼图板ui
        self.board_widget = PuzzleBoard()
        self.board_init_x = int(-self.board_widget.width() / 2)
        self.board_init_y = int(-self.board_widget.height() / 2)
        settings.view_position = (self.board_init_x,self.board_init_y)
        self.board_widget.setGeometry(self.board_init_x, self.board_init_y, self.board_widget.width(), self.board_widget.height())
        self.scale(settings.init_scale, settings.init_scale)
        self.scene.addWidget(self.board_widget)
        self.setMouseTracking(False)

        # 信号槽连接
        self.scale_reset_signal.connect(self.scaleReset)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pass  # self.board_widget.mousePress_handler(event)
        settings.is_pressing_middle = event.button() == Qt.MiddleButton
        settings.start_view_position = (event.localPos().x(),event.localPos().y())

    def mouseReleaseEvent(self, event):  # 鼠标键释放时调用
        settings.is_pressing_middle = False
        settings.view_position = (self.board_widget.x(), self.board_widget.y())

    def mouseMoveEvent(self, event):  # 鼠标移动事件
        if settings.is_pressing_middle:
            x = settings.view_position[0] + (event.localPos().x() -
                                             settings.start_view_position[0])*settings.view_move_speed
            y = settings.view_position[1] + (event.localPos().y() -
                                             settings.start_view_position[1])*settings.view_move_speed
            self.board_widget.setGeometry(x,y, self.board_widget.width(), self.board_widget.height())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            settings.zoom_scale = 4

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            settings.zoom_scale = 1

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, event.angleDelta().y() / 2500.0 * settings.zoom_scale))

    def scaleReset(self):
        self.board_widget.setGeometry(self.board_init_x, self.board_init_y, self.board_widget.width(), self.board_widget.height())
        self.scaleView((1/settings.scale)*settings.init_scale)

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        settings.scale *= scaleFactor
        self.scale(scaleFactor, scaleFactor)
        settings.scale_changed = True
        QApplication.processEvents()
