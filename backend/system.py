import os, sys
import winreg, json
import psutil
import ctypes
import inspect


def program_dir():
    return sys._MEIPASS + "/" if hasattr(sys, 'frozen') else os.getcwd() + "/"


def file_size(file_path):
    if not os.path.exists(file_path): return -1
    fsize = os.path.getsize(file_path)
    f_kb = fsize / float(1024)
    return f_kb


def get_desktop():
    # 获取电脑桌面路径
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders', )
    return winreg.QueryValueEx(key, "Desktop")[0]


# 保存数据，格式为json
def save_json(filename, value=None, overwrite=True):
    with open(filename, 'w' if overwrite else 'a',encoding='utf-8') as f:
        if value != None: f.write(json.dumps(value))


# 查找进程是否已运行
def proc_exist():
    process_name = os.path.basename(sys.executable)
    if process_name == "python.exe": return False  # 避开python运行时
    pl = psutil.pids()
    proc_num = len([0 for pid in pl if psutil.Process(pid).name() == process_name])
    return proc_num > 2

# 强行杀死线程
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0: raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


# 强行杀死线程
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


