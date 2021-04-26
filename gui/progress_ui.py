from threading import Thread
from multiprocessing import Queue
from _queue import Empty
from PyQt5.QtCore import Qt, pyqtSignal

from gui.base import BaseDialog,UpdateThread


class ProgressDialog(BaseDialog):
    queue = Queue()
    complete_signal = pyqtSignal()

    def __init__(self,task_fun,text_width,*args,**kwargs):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(text_width+10,self.height())
        self.progressBar.setFixedWidth(text_width)
        self.task_label.setFixedWidth(text_width)
        self.status_label.setFixedWidth(text_width)

        self.task_thread = Thread(target=task_fun, args=(self.queue,*args), kwargs=kwargs)
        self.task_thread.start()
        self.update_thread = UpdateThread(self)
        self.update_thread.refresh_signal.connect(self.refresh_ui)
        self.update_thread.start()

    def refresh_ui(self):
        try:
            progress, status, task_name, is_finished = self.queue.get_nowait()
            self.progressBar.setValue(progress)
            self.status_label.setText(status)
            self.task_label.setText(task_name)
            if is_finished:
                self.complete_signal.emit()
                self.update_thread.running = False
                self.update_thread.exit(0)
                self.close()
        except Empty: pass