import atexit
import subprocess


class Runner:
    def __init__(self, args, log, at_exit_kill=True):
        self.args = args
        self.log = log
        self.at_exit_kill = at_exit_kill
        self.p = None

    def start(self):
        # ----- Using Python subprocess
        # For now, PIPE are not used as we cannot use them to communicate
        # DedicatedCustomServer.Starter does not use standard I/O
        if self.p is not None and self.p.poll() != 0:
            self.log('Cannot start server if a server is already running',
                     level='ERROR')
            return self.p.pid

        self.p = subprocess.Popen(self.args,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)
        # Optional, kill server if Python exit
        if self.at_exit_kill:
            atexit.register(self.p.kill)

        self.log('process PID', self.p.pid)
        return self.p.pid

    def stop(self):
        if self.p is None:
            return None
        self.p.kill()
        code = self.p.returncode
        self.p = None
        return code

    def status(self):
        return self.p.poll()

    def restart(self):
        self.stop()
        self.start()
        return

# ----- Using pywin32
# Not used for now, but may be useful in the future for better access to I/O
'''
p = win32process.CreateProcess(None,
                               args,
                               None,
                               None,
                               0,
                               win32process.NORMAL_PRIORITY_CLASS,
                               None,
                               None,
                               StartupInfo)
# Optional, kill server if Python exit
atexit.register(win32process.TerminateProcess, p[0], 0)
'''
