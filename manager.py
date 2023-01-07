import sys

import win32gui
import win32con
import win32process

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        # for development purpose
        self.debug = False
        # class members
        self.status = 'uninitialized'
        self.window_list = []
        self.hwnd = 0
        # initialize
        self.reinitialize()

    def reinitialize(self):
        self.window_list = []
        self.hwnd = 0
        self.update_status('waiting for window selection')

    def update_status(self, status):
        self.status = status
        self.label_window_status.setText(self.status)

    def ready(self):
        pid = win32process.GetWindowThreadProcessId(self.hwnd)
        return pid[0] > 0

    def send_message(self, message):
        if self.ready():
            for c in message:
                win32gui.SendMessage(self.hwnd, win32con.WM_CHAR, ord(c), None)
            win32gui.SendMessage(self.hwnd, win32con.WM_CHAR, win32con.VK_RETURN, None)
        else:
            print('not ready')
            self.update_status('waiting for window selection')

    def window_refresh(self):
        self.reinitialize()

        # List windows with "server" in title
        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                win_text = win32gui.GetWindowText(hwnd)
                if 'server' in win_text.lower() or self.debug:
                    self.window_list.append((win_text, hwnd))
        win32gui.EnumWindows(enum_windows_callback, None)

        # update window list
        self.comboBox_window_list.clear()
        window_list = []
        for text, hwnd in self.window_list:
            window_list.append(f'[{hwnd:10}] {text}')
        self.comboBox_window_list.addItems(window_list)

    def window_select(self):
        self.hwnd = 0

        selection = self.comboBox_window_list.currentIndex()
        if selection < 0:
            print('no window selected')
        else:
            text, hwnd = self.window_list[selection]
            self.hwnd = hwnd
            self.update_status(f'selected window : {hwnd}')

    def message_checkbox(self):
        print('message_checkbox')

    def message_send(self):
        print('message_send')

    def quick_cmd_send(self):
        cmd = self.lineEdit_quick_cmd.text()
        self.send_message(cmd)

    def quick_warmup_set(self):
        print('quick_warmup_set')

    def quick_map_set(self):
        print('quick_map_set')

    def culture_checkbox(self):
        print('culture_checkbox')

    def culture_set(self):
        print('culture_set')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
