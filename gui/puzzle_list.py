#coding=utf-8
import time

from PyQt5.QtWidgets import QListWidget, QListView, QListWidgetItem,QLabel
from PyQt5.QtGui import QPixmap, QDrag, QIcon
from PyQt5.QtCore import QSize, Qt, QByteArray, QDataStream, QIODevice, QPoint, QVariant, QMimeData, QSizeF, pyqtSignal

from gui.base import BaseImage,BasePixmap
from backend.settings import settings


class PuzzleListWidget(QListWidget):

    def __init__(self):
        super().__init__()
        self.size = settings.piece_size*settings.scale
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setViewMode(QListView.IconMode)
        self.setSpacing(5)

        for i in range(len(settings.pieces)):
            self.addPiece(i)
            settings.pieces_index_list_not_placed.append(i)

    def resizeEvent(self, event):
        self.addItem(QListWidgetItem())
        self.takeItem(self.count()-1)

    def paintEvent(self,event):
        if settings.scale_changed or settings.refresh_puzzle_list:
            self.clear()
            for i in settings.pieces_index_list_not_placed: self.addPiece(i)
            settings.scale_changed = False
            settings.refresh_puzzle_list = False

    def addPiece(self, index):
        pix = BasePixmap(settings.pieces[index],scale=settings.scale)
        puzzleItem = QListWidgetItem()
        self.size = settings.piece_size*settings.scale
        img_label = QLabel(); img_label.setPixmap(pix)
        puzzleItem.setSizeHint(QSize(self.size,self.size))
        puzzleItem.setData(Qt.UserRole, QVariant(index))
        puzzleItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
        self.addItem(puzzleItem)
        self.setItemWidget(puzzleItem, img_label)

    def dropEvent(self, event):
        if event.mimeData().hasFormat("image/x-puzzle-xdbcb8"):
            piece = event.mimeData().data("image/x-puzzle-xdbcb8")
            dataStream = QDataStream(piece, QIODevice.ReadOnly)
            index = dataStream.readInt16(); self.addPiece(index)
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, DropActions):
        item = self.currentItem()
        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        pieceIndex = item.data(Qt.UserRole)
        dataStream.writeInt16(pieceIndex)
        mimeData = QMimeData()
        mimeData.setData("image/x-puzzle-xdbcb8", itemData)

        piecePix = BasePixmap(settings.pieces[pieceIndex], scale=settings.scale)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QPoint(piecePix.width()/2, piecePix.height()/2))
        drag.setPixmap(piecePix)

        if drag.exec_(Qt.MoveAction) == Qt.MoveAction:
            moveItem = self.takeItem(self.row(item))
            del moveItem

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("image/x-puzzle-xdbcb8"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("image/x-puzzle-xdbcb8"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()