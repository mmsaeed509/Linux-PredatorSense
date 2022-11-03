import os

from PyQt5 import QtWidgets, QtGui
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor

from frontend import Ui_PredatorSense
from ecwrite import ec_write, ec_read
import enum

GPU_FAN_MODE_CONTROL = '0x21'
GPU_AUTO_MODE = '0x50'
GPU_TURBO_MODE = '0x60'
GPU_MANUAL_MODE = '0x70'
GPU_MANUAL_SPEED_CONTROL = '0x3A'
COOL_BOOST_CONTROL = '0x10'
COOL_BOOST_ON = '0x01'
COOL_BOOST_OFF = '0x00'
CPU_FAN_MODE_CONTROL = '0x22'
CPU_AUTO_MODE = '0x54'
CPU_TURBO_MODE = '0x58'
CPU_MANUAL_MODE = '0x5C'
CPU_MANUAL_SPEED_CONTROL = '0x37'
FAN_PROFILE_CONTROL = '0x29'
FAN_PROFILE_NORMAL = '0x00'
FAN_PROFILE_PERF = '0x01'
FAN_PROFILE_AGGR = '0x02'


class PFS(enum.Enum):  # ProcessorFanState
    Manual = 0
    Auto = 1
    Turbo = 2


class MainWindow(QtWidgets.QDialog, Ui_PredatorSense):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.cb = ec_read(int(COOL_BOOST_CONTROL, 0)) == 1
        if self.cb:
            self.coolboost_checkbox.setChecked(True)

        t = int(ec_read(int(CPU_FAN_MODE_CONTROL, 0)))
        t1 = False

        if t == 84 or t == 00:
            self.cpuFanMode = PFS.Auto
            self.cpu_auto.setChecked(True)
        elif t == 88:
            self.cpuFanMode = PFS.Turbo
            self.cpu_turbo.setChecked(True)
            t1 = True
        elif t == 92 or t == 93:
            self.cpuFanMode = PFS.Manual
            self.cpu_manual.setChecked(True)
        else:
            print('FOUND', t)
            print('UNKNOWN VALUE FOUND EXIT at cpu box')
            self.cpuauto()

        t = int(ec_read(int(GPU_FAN_MODE_CONTROL, 0)))
        t2 = False

        if t == 80 or t == 00:
            self.gpuFanMode = PFS.Auto
            self.gpu_auto.setChecked(True)
        elif t == 96:
            self.gpuFanMode = PFS.Turbo
            t2 = True
            self.gpu_turbo.setChecked(True)
        elif t == 112:
            self.gpuFanMode = PFS.Manual
            self.gpu_manual.setChecked(True)
        else:
            print('FOUND', t)
            print('UNKNOWN VALUE FOUND EXIT at gpu box')
            self.gpuauto()

        if t1 and t2:
            self.global_turbo.setChecked(True)

        self.cpu_auto.toggled['bool'].connect(self.cpuauto)
        self.cpu_turbo.toggled.connect(self.cpumax)
        self.gpu_auto.toggled.connect(self.gpuauto)
        self.gpu_turbo.toggled.connect(self.gpumax)
        self.coolboost_checkbox.clicked['bool'].connect(self.toggleCB)
        self.verticalSlider.valueChanged.connect(self.cpumanual)
        self.verticalSlider_2.valueChanged.connect(self.gpumanual)
        self.cpu_manual.toggled.connect(self.cpusetmanual)
        self.gpu_manual.toggled.connect(self.gpusetmanual)
        self.exit_button.clicked.connect(lambda: sys.exit(0))

    def cpumax(self):
        ec_write(int(CPU_FAN_MODE_CONTROL, 0), int(CPU_TURBO_MODE, 0))
        self.cpuFanMode = PFS.Turbo

    def gpumax(self):
        ec_write(int(GPU_FAN_MODE_CONTROL, 0), int(GPU_TURBO_MODE, 0))
        self.gpuFanMode = PFS.Turbo

    def cpuauto(self):
        ec_write(int(CPU_FAN_MODE_CONTROL, 0), int(CPU_AUTO_MODE, 0))
        self.cpuFanMode = PFS.Auto

    def gpuauto(self):
        ec_write(int(GPU_FAN_MODE_CONTROL, 0), int(GPU_AUTO_MODE, 0))
        self.gpuFanMode = PFS.Auto

    def toggleCB(self, tog):
        print('CoolBoost Toggle: ', end='')
        if tog:
            print('On')
            ec_write(int(COOL_BOOST_CONTROL, 0), int(COOL_BOOST_ON, 0))
        else:
            print('Off')
            ec_write(int(COOL_BOOST_CONTROL, 0), int(COOL_BOOST_OFF, 0))

    def cpumanual(self, level):
        print(str(level * 10), end=', ')
        print(hex(level * 10))
        ec_write(int(CPU_MANUAL_SPEED_CONTROL, 0), level * 10)

    def gpumanual(self, level):
        print(level * 10, end=', ')
        print(hex(level * 10))
        ec_write(int(GPU_MANUAL_SPEED_CONTROL, 0), level * 10)

    def cpusetmanual(self):
        ec_write(int(CPU_FAN_MODE_CONTROL, 0), int(CPU_MANUAL_MODE, 0))
        self.cpuFanMode = PFS.Manual

    def gpusetmanual(self):
        ec_write(int(GPU_FAN_MODE_CONTROL, 0), int(GPU_MANUAL_MODE, 0))
        self.gpuFanMode = PFS.Manual


app = QtWidgets.QApplication([])
application = MainWindow()
application.setFixedSize(635, 465) # Makes the window not resizeable
app.setStyle('Breeze')

# Dark theme implementation
palette = QPalette()
palette.setColor(QPalette.Window, QColor(53, 53, 53))
palette.setColor(QPalette.WindowText, Qt.white)
palette.setColor(QPalette.Base, QColor(25, 25, 25))
palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ToolTipBase, Qt.black)
palette.setColor(QPalette.ToolTipText, Qt.white)
palette.setColor(QPalette.Text, Qt.white)
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.red)
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, Qt.black)
app.setPalette(palette)

# Required for the app to have its icon when bundled with PyInstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


application.setWindowIcon(QtGui.QIcon(resource_path('app_icon.ico')))
application.show()
sys.exit(app.exec())
