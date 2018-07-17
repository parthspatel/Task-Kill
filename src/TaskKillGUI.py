import os
import sys
import ctypes
import time

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except:
    os.system('pip install pyqt5')
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *


PAD_SIZE = 20


class TaskKillThread(QThread):

    def __init__(self, shelfName='paths.tmr'):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            #/im MapleStory.exe
            os.system('''taskkill /f /fi "status eq not responding" /t''')
            time.sleep(10)


class TaskKiller(QMainWindow):

    def __init__(self):
        super().__init__()

        self.title = 'Task Killer'

        QCoreApplication.setOrganizationName('Parth S. Patel')
        QCoreApplication.setOrganizationDomain('https://github.com/parthspatel/Task-Kill')
        QCoreApplication.setApplicationName('Task Killer')

        self.left = 100
        self.top = 100
        self.width = 300
        self.height = 300

        self.initUI()

        self.startEvent()

        self.myThread = TaskKillThread()
        self.myThread.start()

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('./logo.png'))

    def startEvent(self):
        self.showNormal()

    def closeEvent(self, event):
        self.closeThreads()  # Close all the threads

    def closeThreads(self):
        self.myThread.quit()


def isUserAdmin():
    # type: () -> bool
    """
    Return True if user has admin privileges.

    Raises:
        AdminStateUnknownError if user privileges cannot be determined.
    """
    try:
        return os.getuid() == 0
    except AttributeError:
        pass
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        raise AdminStateUnknownError


def runApp(QTApp):
    app = QApplication(sys.argv)
    ui = QTApp()
    ui.show()
    return app.exec_()


def closeApp(app):
    sys.exit(app)


if __name__ == '__main__':
    if not isUserAdmin():
        print("> User account does not have admin controls, rerunning with admin controls")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    app = runApp(TaskKiller)
    closeApp(app)
