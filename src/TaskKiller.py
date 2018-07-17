import os
import sys
import ctypes
import re
import time
from datetime import datetime
from subprocess import Popen, PIPE, check_output

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

    def __init__(self, process_name_line_edit=None, time_to_wait=None):
        QThread.__init__(self)
        self.process_name_line_edit = process_name_line_edit
        self.time_to_wait = time_to_wait

    def __del__(self):
        self.wait()

    def get_processes_not_responsive(self):
        """
        Takes tasklist output and parses the table into a dict
        """
        tasks = check_output('tasklist /fi "status eq not responding"').decode('cp866', 'ignore').split("\r\n")
        p = []
        for task in tasks:
            m = re.match(b'(.*?)\\s+(\\d+)\\s+(\\w+)\\s+(\\w+)\\s+(.*?)\\s.*', task.encode())
            if m is not None:
                p.append({'name': m.group(1).decode(),
                          'pid': int(m.group(2).decode()),
                          'session_name': m.group(3).decode(),
                          'session_num': int(m.group(4).decode()),
                          'mem_usage': int(m.group(5).decode('ascii', 'ignore').replace(',', ''))
                          })
        return(p)

    def run(self):
        cache = {}
        while True:
            # Initalize Variables
            try:
                time_to_wait = self.time_to_wait.text()
                time_to_wait = int(time_to_wait)
            except:
                time_to_wait = 60

            process_name = self.process_name_line_edit.text()

            # Clean cache and force close
            for entry in list(cache):
                print(entry)
                print(time.time() - cache[entry][1])
                if time.time() - cache[entry][1] > time_to_wait:
                    print('{}s have passed for: {}\tPID: {}'.format(time_to_wait, entry, cache[entry][0]))
                    try:
                        if process_name in entry or process_name is None:
                            print('Closing: Name: {}\tPID: {}'.format(entry, cache[entry][0]))
                            os.system('taskkill /PID {} /f'.format(cache[entry][0]))
                            del cache[entry]
                    except KeyError:
                        continue

            # Get all non-responding processes
            processes = self.get_processes_not_responsive()

            # Add to cache
            for process in processes:
                if process['name'] in cache:
                    continue
                cache.update({process['name']: [process['pid'], time.time()]})

            time.sleep(5)


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

        self.myThread = TaskKillThread(process_name_line_edit=self.ProcessLineEdit,
                                       time_to_wait=self.TimeLineEdit)
        self.myThread.start()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('./logo.png'))

        # Process Name Label
        self.ProcessLabel = QLabel(self)
        self.ProcessLabel.setText('Process Name: ')
        self.ProcessLabel.move(PAD_SIZE, PAD_SIZE * 2)

        # Process Name Line Edit
        self.ProcessLineEdit = QLineEdit(self)
        self.ProcessLineEdit.setPlaceholderText('Process Name')
        self.ProcessLineEdit.setReadOnly(False)
        self.ProcessLineEdit.move(PAD_SIZE + self.ProcessLabel.x() + self.ProcessLabel.width(), self.ProcessLabel.y())

        # Time To Wait Label
        self.TimeLabel = QLabel(self)
        self.TimeLabel.setText('Time to Wait: ')
        self.TimeLabel.move(PAD_SIZE + self.ProcessLineEdit.x() + self.ProcessLineEdit.width(), self.ProcessLineEdit.y())

        # Time To Wait Line Edit
        self.TimeLineEdit = QLineEdit(self)
        self.TimeLineEdit.setText('60')
        self.TimeLineEdit.setReadOnly(False)
        self.TimeLineEdit.move(PAD_SIZE + self.TimeLabel.x() + self.TimeLabel.width(), self.TimeLabel.y())

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
