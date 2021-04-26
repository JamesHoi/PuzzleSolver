# coding=utf-8

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect, QDataStream, QIODevice, Qt, pyqtSignal, QPoint, QByteArray, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QPainter, QColor, QCursor, QMouseEvent

from gui.base import BasePixmap
from backend.settings import settings


class PuzzleBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(settings.pic_width, settings.pic_height)
        self.highlightedRect = QRect()
        self.setAcceptDrops(True)

    def targetSquare(self, position):
        x = position.x() // settings.piece_size * settings.piece_size
        y = position.y() // settings.piece_size * settings.piece_size
        return QRect(x, y, settings.piece_size, settings.piece_size)

    def findPiece(self, piece_Rect):
        try:
            return settings.pieces_rect_list.index(piece_Rect)
        except ValueError:
            return -1

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("image/x-puzzle-xdbcb8"):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        updateRect = self.highlightedRect
        self.highlightedRect = QRect()
        self.update(updateRect)
        event.accept()

    def dragMoveEvent(self, event):
        updateRect = self.highlightedRect.united(self.targetSquare(event.pos()))
        if event.mimeData().hasFormat("image/x-puzzle-xdbcb8") and self.findPiece(self.targetSquare(event.pos())) == -1:
            self.highlightedRect = self.targetSquare(event.pos())
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            self.highlightedRect = QRect()
            event.ignore()
        self.update(updateRect)

    def dropEvent(self, event):
        if event.mimeData().hasFormat("image/x-puzzle-xdbcb8") and self.findPiece(self.targetSquare(event.pos())) == -1:
            pieceData = event.mimeData().data("image/x-puzzle-xdbcb8")
            dataStream = QDataStream(pieceData, QIODevice.ReadOnly)
            square = self.targetSquare(event.pos())
            settings.pieces_index_list.append(dataStream.readInt16())
            settings.pieces_rect_list.append(square)

            self.highlightedRect = QRect()
            self.update(square)
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            self.highlightedRect = QRect()
            event.ignore()

    def mousePress_handler(self, event):
        square = self.targetSquare(event.pos())
        found = self.findPiece(square)
        if found == -1:
            return
        piece_index = settings.pieces_index_list[found]

        # 删除
        del settings.pieces_index_list[found]
        del settings.pieces_rect_list[found]
        self.update(square)

        # 添加信息
        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream.writeInt16(piece_index)
        mimeData = QMimeData()
        mimeData.setData("image/x-puzzle-xdbcb8", itemData)

        # 拖拉设置
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - square.topLeft())
        drag.setPixmap(BasePixmap(settings.pieces[piece_index], scale=settings.scale))

        tmp = drag.exec_(Qt.MoveAction)
        if tmp != Qt.MoveAction:
            settings.pieces_index_list.insert(found, piece_index)
            settings.pieces_rect_list.insert(found, square)
            self.update(self.targetSquare(event.pos()))

    def mousePressEvent(self, event):
        self.mousePress_handler(event)

    def paintEvent(self, event):
        painter = QPainter(); painter.begin(self)
        num = settings.pieces_num;size = settings.piece_size
        rows = settings.pic_rows;columns = settings.pic_columns

        painter.fillRect(event.rect(), Qt.white)
        # 画网格线
        [r, g, b] = [c for c in settings.grid_color]
        painter.setPen(QColor(r,g,b))
        for i in range(columns+1):
            x = i*size; y0 = 0; y1 = settings.pic_height
            painter.drawLine(QPoint(x,y0),QPoint(x,y1))
        for i in range(rows+1):
            y = i*size; x0 = 0; x1 = settings.pic_width
            painter.drawLine(QPoint(x0,y),QPoint(x1,y))
        # 画背景图
        if settings.bg_img is not None:
            painter.drawPixmap(0, 0, self.width(), self.height(), settings.bg_img)
        # 拼图放在拼图板上的效果
        if self.highlightedRect.isValid():
            painter.setBrush(QColor("#E6E6FA"))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.highlightedRect.adjusted(0, 0, -1, -1))
        for i in range(len(settings.pieces_rect_list)):
            painter.drawPixmap(settings.pieces_rect_list[i],
                               BasePixmap(settings.pieces[settings.pieces_index_list[i]]))
        painter.end()
