import os
import sys

import win32gui
import win32con
import win32process

from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui import Ui_MainWindow
from log import Log
from runner import Runner

log = Log('ManagerLogs.txt')


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
        self.server = None
        # timer for message spammer
        self.timer_msg_spam = QtCore.QTimer(self)
        self.timer_msg_spam.timeout.connect(self.message_send)
        # timer for culture team
        self.timer_culture = QtCore.QTimer(self)
        self.timer_culture.setInterval(1000)
        self.timer_culture.timeout.connect(self.culture_set)
        # timer for server runner
        self.timer_runner = QtCore.QTimer(self)
        self.timer_runner.setInterval(1000)
        self.timer_runner.timeout.connect(self.server_runner)
        # initialize
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
                log('not ready')
                self.update_status('waiting for window selection')

    def window_refresh(self):
        self.window_list = []
        self.hwnd = 0
        self.update_status('waiting for window selection')

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
            log('no window selected')
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

    def runner_checkbox(self):
        if self.checkBox_runner.isChecked():
            self.timer_runner.start()
        else:
            self.timer_runner.stop()

    def runner_restart(self):
        if self.server is not None:
            self.server.stop()

        server_folder = self.lineEdit_runner_folder.text()
        server_starter = self.lineEdit_runner_starter.text()
        server_config_file = self.lineEdit_runner_config.text()
        server_options = self.lineEdit_runner_options.text()

        if not os.path.isdir(server_folder):
            log('NotADirectoryError', level='ERROR')
            return
        if not os.path.isfile(server_folder + server_starter):
            log('FileNotFoundError', level='ERROR')
            return

        os.chdir(server_folder)
        args = [f'{server_starter}', f'/dedicatedcustomserverconfigfile', f'{server_config_file}', server_options]
        log('arguments sequence', args)

        self.server = Runner(args, log)
        self.server.restart()

        if not self.checkBox_runner.isChecked():
            QtTest.QTest.qWait(500)
            self.runner_window_update()

    def runner_window_update(self):
        def enum_windows_callback(hwnd, extra):
            threadid, pid = win32process.GetWindowThreadProcessId(hwnd)
            if self.server.p.pid == pid:
                self.hwnd = hwnd
                self.update_status(f'selected window : {hwnd}')

        win32gui.EnumWindows(enum_windows_callback, None)

    def server_runner(self):
        # checkbox checked ?
        if not self.checkBox_runner.isChecked():
            return
        # server never started ?
        if self.server is None:
            self.runner_restart()
            return
        # server crashed ?
        if self.server.status() is not None:
            self.runner_restart()
            return
        self.runner_window_update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
