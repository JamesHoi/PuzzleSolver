from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtCore import Qt, pyqtSignal

from gui.base import BaseDialog


class ParamDialog(BaseDialog):
    complete_signal = pyqtSignal(list)

    def __init__(self, param_text,text_width):
        super(ParamDialog, self).__init__()
        self.param_label.setText(param_text)
        self.setFixedSize(text_width+40, self.height())
        self.lineEdit.setFixedWidth(text_width)
        self.param_label.setFixedWidth(text_width)
        self.warning_label.setFixedWidth(text_width)
        width = self.buttonBox.width(); height = self.buttonBox.height()
        self.buttonBox.setGeometry(self.lineEdit.width()+self.lineEdit.x()-width,self.buttonBox.y(),width,height)

        self.setWindowModality(Qt.ApplicationModal)
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
        self.buttonBox.accepted.connect(self.accepted_handler)
        self.buttonBox.rejected.connect(self.rejected_handler)

    def accepted_handler(self):
        self.close()
        self.complete_signal.emit(self.lineEdit.text().split(";"))

    def rejected_handler(self):
        self.close()
        self.complete_signal.emit([])