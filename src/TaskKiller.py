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

    def __init__(self, line_edit=None):
        QThread.__init__(self)
        self.line_edit = line_edit

    def __del__(self):
        self.wait()

    def run(self):
        cmd = r'taskkill /f /fi "status eq not responding"'
        while True:
            process_name = self.line_edit.text()
            if process_name:
                os.system(cmd + ' /im ' + str(process_name) + ' /t')
            else:
                os.system(cmd + ' /t')
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

        self.myThread = TaskKillThread(line_edit=self.ProcessLineEdit)
        self.myThread.start()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('./logo.png'))

        # Process Name Label
        # Server Status Img
        self.ProcessLabel = QLabel(self)
        self.ProcessLabel.setText('Process Name: ')
        self.ProcessLabel.move(PAD_SIZE, PAD_SIZE * 2)

        # Process Name Line Edit
        self.ProcessLineEdit = QLineEdit(self)
        self.ProcessLineEdit.setPlaceholderText('Process Name')
        self.ProcessLineEdit.setReadOnly(False)

        self.ProcessLineEdit.move(PAD_SIZE + self.ProcessLabel.x() + self.ProcessLabel.width(), self.ProcessLabel.y())

    def startEvent(self):
        self.showNormal()
        self.__readAndApplyWindowAttributeSettings()

    def closeEvent(self, event):
        self.closeThreads()
        self.__writeWindowAttributeSettings()

    def closeThreads(self):
        self.myThread.quit()

    def __readAndApplyWindowAttributeSettings(self):
        '''
        Read window attributes from settings,
        using current attributes as defaults (if settings not exist.)

        Called at QMainWindow initialization, before show().
        '''
        qsettings = QSettings()

        qsettings.beginGroup('mainWindow')

        # No need for toPoint, etc. : PySide converts types
        self.restoreGeometry(qsettings.value('geometry', self.saveGeometry()))
        self.restoreState(qsettings.value('saveState', self.saveState()))
        self.move(qsettings.value('pos', self.pos()))
        self.resize(qsettings.value('size', self.size()))

        self.ProcessLineEdit.setText(qsettings.value('processName'))

        qsettings.endGroup()

    def __writeWindowAttributeSettings(self):
        '''
        Save window attributes as settings.

        Called when window moved, resized, or closed.
        '''
        qsettings = QSettings()

        qsettings.beginGroup('mainWindow')
        qsettings.setValue('geometry', self.saveGeometry())
        qsettings.setValue('saveState', self.saveState())
        qsettings.setValue('maximized', self.isMaximized())
        if not self.isMaximized() == True:
            qsettings.setValue('pos', self.pos())
            qsettings.setValue('size', self.size())
        qsettings.setValue('processName', self.ProcessLineEdit.text())

        qsettings.endGroup()


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
