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
        # timer for message spammer
        self.timer_msg_spam = QtCore.QTimer(self)
        self.timer_msg_spam.timeout.connect(self.message_send)
        # timer for culture team
        self.timer_culture = QtCore.QTimer(self)
        self.timer_culture.setInterval(1000)
        self.timer_culture.timeout.connect(self.culture_set)
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
        if len(message) > 0:
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
        self.timer_msg_spam.setInterval(self.spinBox_spammer_ms.value())
        if self.checkBox_spammer.isChecked():
            self.timer_msg_spam.start()
        else:
            self.timer_msg_spam.stop()

    def message_send(self):
        lines = self.plainTextEdit_message.toPlainText().split('\n')
        for line in lines:
            if len(line) > 0:
                self.send_message(f'say {line}')

    def quick_cmd_send(self):
        cmd = self.lineEdit_quick_cmd.text()
        self.send_message(cmd)

    def quick_warmup_set(self):
        value = self.spinBox_quick_warmuptime.value()
        self.send_message(f'WarmupTimeLimit {value}')

    def quick_map_set(self):
        value = self.lineEdit_quick_map.text()
        self.send_message(f'Map {value}')

    def culture_checkbox(self):
        if self.checkBox_culture_team_auto.isChecked():
            self.timer_culture.start()
        else:
            self.timer_culture.stop()

    def culture_set(self):
        culture_team_1 = self.comboBox_culture_team_1.currentText()
        culture_team_2 = self.comboBox_culture_team_2.currentText()
        self.send_message(f'CultureTeam1 {culture_team_1}')
        self.send_message(f'CultureTeam2 {culture_team_2}')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
