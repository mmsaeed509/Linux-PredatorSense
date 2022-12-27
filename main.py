import os

from PyQt5 import QtWidgets, QtGui
import sys

from PyQt5.QtCore import Qt, QTimer, QProcess
from PyQt5.QtGui import QPalette, QColor

from frontend import Ui_PredatorSense
from ecwrite import *
import enum

##------------------------------##
##--Predator EC Register Class--##
# ECState
class ECS(enum.Enum):
    # COOL_BOOST_CONTROL = '0x10'
    # COOL_BOOST_ON = '0x01'
    # COOL_BOOST_OFF = '0x00'

    GPU_FAN_MODE_CONTROL = '0x21'
    GPU_AUTO_MODE = '0x50'
    GPU_TURBO_MODE = '0x60'
    GPU_MANUAL_MODE = '0x70'
    GPU_MANUAL_SPEED_CONTROL = '0x3A'

    CPU_FAN_MODE_CONTROL = '0x22'
    CPU_AUTO_MODE = '0x54'
    CPU_TURBO_MODE = '0x58'
    CPU_MANUAL_MODE = '0x5C'
    CPU_MANUAL_SPEED_CONTROL = '0x37'

    KB_30_SEC_AUTO = '0x06'
    KB_30_AUTO_OFF = '0x00'
    KB_30_AUTO_ON = '0x1E'

    TURBO_LED_CONTROL = '0x5B'
    TURBO_LED_ON = '0x01'
    TURBO_LED_OFF = '0x00'

    CPUFANSPEEDHIGHBITS = '0x13'
    CPUFANSPEEDLOWBITS = '0x14'
    GPUFANSPEEDHIGHBITS = '0x15'
    GPUFANSPEEDLOWBITS = '0x16'

    CPUTEMP = '0xB0'
    GPUTEMP = '0xB7'
    SYSTEMP = '0xB3'

    POWERSTATUS = '0x00'
    POWERPLUGGEDIN = '0x01'
    POWERUNPLUGGED = '0x00'

    BATTERYCHARGELIMIT = '0x03'
    BATTERYLIMITON = '0x51'
    BATTERYLIMITOFF = '0x11'

    BATTERYSTATUS = '0xC1'
    BATTERYPLUGGEDINANDCHARGING = '0x02'
    BATTERYDRAINING ='0x01'
    BATTERYOFF = '0x00'

    POWEROFFUSBCHARGING = '0x08'
    USBCHARGINGON = '0x0F'
    USBCHARGINGOFF = '0x1F'

    LCDOVERDRIVE = '0x21' # (0x_0 = off, 0x_8 = on) - high bit

    PREDATORMODE = '0x2C'
    QUIETMODE = '0x00'
    DEFAULTMODE = '0x01'
    EXTREMEMODE = '0x04'
    TURBOMODE = '0x05'

    TRACKPADSTATUS = '0xA1'
    TRACKPADENABLED = '0x00'
    TRACKPADDISABLED = '0x04'

##------------------------------##
##-------Predator Fan Mode------##
# ProcessorFanState
class PFS(enum.Enum):  
    Manual = 0
    Auto = 1
    Turbo = 2    

##------------------------------##
##---------Undervolting---------##
UNDERVOLT_PATH = "<user_path>/.local/lib/python3.8/site-packages/undervolt.py"

COREOFFSET = 90 # mV
CACHEOFFSET = 90 # mV
minrecordedVoltage = 20.0 # V
maxrecordedVoltage = 0 # V

## Read the current undervoltage offsets
def checkUndervoltStatus(self):
    process = QProcess()
    process.start('sudo python ' + UNDERVOLT_PATH + ' -r')
    process.waitForStarted()
    process.waitForFinished()
    process.waitForReadyRead()
    underVoltStatus = process.readAll()
    process.close()
    
    underVoltStatus = str(underVoltStatus, 'utf-8')
    # print(underVoltStatus)
    self.undervoltStatus.setText(underVoltStatus)

## Apply the undervoltage offsets values
def applyUndervolt(self, core, cache):
    process = QProcess()
    process.start('sudo python ' + UNDERVOLT_PATH + ' --core -' + str(core) + ' --cache -' + str(cache))
    process.waitForStarted()
    process.waitForFinished()
    process.waitForReadyRead()
    process.close()

    global minrecordedVoltage
    global maxrecordedVoltage
    minrecordedVoltage = 20.0
    maxrecordedVoltage = 0

    checkUndervoltStatus(self)

## Update the current VCore
def checkVoltage(self):
    process = QProcess()
    process.start('sudo rdmsr 0x198 -p 0 -u --bitfield 47:32') # Processor 0
    # process.start('sudo rdmsr 0x198 -a -u --bitfield 47:32') # All processors
    process.waitForStarted()
    process.waitForFinished()
    process.waitForReadyRead()
    voltage = process.readAll()
    process.close()

    ## https://askubuntu.com/questions/876286/how-to-monitor-the-vcore-voltage
    # print(voltage)
    voltage = int(voltage)/8192

    global minrecordedVoltage
    global maxrecordedVoltage
    if voltage < minrecordedVoltage:
        minrecordedVoltage = voltage
    if voltage > maxrecordedVoltage:
        maxrecordedVoltage = voltage

    minmaxVoltages = str("%1.2f" % minrecordedVoltage) + " / " + str("%1.2f" % maxrecordedVoltage)
    # print(minmaxVoltages)

    self.voltageValue.setText(str("%1.2f" % voltage))
    self.voltageMinMaxValue.setText(minmaxVoltages)

##------------------------------##
##-------Main QT Window---------##
class MainWindow(QtWidgets.QDialog, Ui_PredatorSense):

    def __init__(self):
        self.turboEnabled = False
        self.cpufanspeed = 0
        self.gpufanspeed = 0
        self.cpuTemp = 0
        self.gpuTemp = 0
        self.sysTemp = 0

        self.powerPluggedIn = False
        self.onBatteryPower = False
        self.displayOverdrive = False
        self.predatorMode = ECS.DEFAULTMODE.value
        self.usbCharging = ECS.USBCHARGINGON.value

        self.cpuMode = ECS.CPU_AUTO_MODE.value
        self.gpuMode = ECS.GPU_AUTO_MODE.value
        self.cpuFanMode = PFS.Auto
        self.gpuFanMode = PFS.Auto
        self.KB30Timeout = ECS.KB_30_AUTO_OFF.value
        self.trackpad = ECS.TRACKPADENABLED.value

        ## Setup the QT window
        super(MainWindow, self).__init__()
        self.setupUI(self)

        checkUndervoltStatus(self)
        self.ECHandler = ECWrite()
        self.checkPredatorStatus()
        self.checkPowerTempFan()
        self.setupGUI()

        ## Setup new timer to periodically read the EC regsiters and update UI
        self.setUpdateUITimer()

    ## ----------------------------------------------------
    ## Initialise the frame, check all registers and set the appropriate widgets
    def setupGUI(self):
        # if self.cb:
        #     self.coolboost_checkbox.setChecked(True)
        # self.coolboost_checkbox.clicked['bool'].connect(self.toggleCB)

        self.global_auto.clicked.connect(self.setDefaultMode)
        self.global_turbo.clicked.connect(self.setTurboMode)

        self.cpu_auto.clicked.connect(self.cpuauto)
        self.cpu_manual.clicked.connect(self.cpusetmanual)
        self.cpu_turbo.clicked.connect(self.cpumax)
        self.gpu_auto.clicked.connect(self.gpuauto)
        self.gpu_manual.clicked.connect(self.gpusetmanual)
        self.gpu_turbo.clicked.connect(self.gpumax)
        self.cpuManualSlider.valueChanged.connect(self.cpumanual)
        self.gpuManualSlider.valueChanged.connect(self.gpumanual)
        self.exit_button.clicked.connect(self.shutdown)
        self.reset_button.clicked.connect(lambda: applyUndervolt(self, 0, 0))
        self.undervolt_button.clicked.connect(lambda: applyUndervolt(self, COREOFFSET, CACHEOFFSET))

        ## ----------------------------------------------------

        ## We can toggle the register but it does not seem to actually disble the trackpad
        # if self.trackpad == int(TRACKPADENABLED, 0):
        #     self.trackpadCB.setChecked(False)
        # elif self.trackpad == int(TRACKPADDISABLED, 0):
        #     self.trackpadCB.setChecked(True)
        # else:
        #     print("Error read EC register for Trackpad: " + str(self.trackpad))

        ## Set the battery charge indicator
        if self.batteryChargeLimit == int(ECS.BATTERYLIMITON.value, 0):
            self.batteryChargeLimitValue.setText("On")
        elif self.batteryChargeLimit == int(ECS.BATTERYLIMITON.value, 0):
            self.batteryChargeLimitValue.setText("Off")
        else:
            print("Error read EC register for Battery Charge Limit: " + str(self.usbCharging))
    
        ## Set the 30 sec backlight timer
        if self.KB30Timeout == int(ECS.KB_30_AUTO_OFF.value, 0):
            self.KBTimerCB.setChecked(False)
        else:
            self.KBTimerCB.setChecked(True)

        ## Set the LCD overdrive indicator
        # Check if the lower 4 bits equals 8
        overdriveEnabled = self.displayOverdrive & (1 << 3)
        if overdriveEnabled == 0:
            self.LCDOverdriveCB.setChecked(False)
        else:
            self.LCDOverdriveCB.setChecked(True)

        ## Set the USB charging indicator
        if self.usbCharging == int(ECS.USBCHARGINGON.value, 0):
            self.usbChargingCB.setChecked(True)
        elif self.usbCharging == int(ECS.USBCHARGINGOFF.value, 0):
            self.usbChargingCB.setChecked(False)
        else:
            print("Error read EC register for USB Charging: " + str(self.usbCharging))

        self.setPredatorMode()
        self.setFanMode()

        ## ----------------------------------------------------

        self.quietModeCB.clicked['bool'].connect(self.setQuietMode)
        self.defaultModeCB.clicked['bool'].connect(self.setDefaultMode)
        self.extremeModeCB.clicked['bool'].connect(self.setExtremeMode)
        self.turboModeCB.clicked['bool'].connect(self.setTurboMode)

        # self.trackpadCB.clicked['bool'].connect(self.toggletrackpad)
        self.KBTimerCB.clicked['bool'].connect(self.togglekbauto)
        self.LCDOverdriveCB.clicked['bool'].connect(self.toggleLCDOverdrive)
        self.usbChargingCB.clicked['bool'].connect(self.toggleUSBCharging)   

    # Set the current fan and turbo mode
    def setFanMode(self):
        if self.cpuMode == int(ECS.CPU_AUTO_MODE.value, 0):
            self.cpuFanMode = PFS.Auto
            self.cpu_auto.setChecked(True)
        elif self.cpuMode == int(ECS.CPU_TURBO_MODE.value, 0) or self.cpuMode == int('0xA8', 0):
            self.cpuFanMode = PFS.Turbo
            self.cpu_turbo.setChecked(True)
            self.turboEnabled = True
        elif self.cpuMode == int(ECS.CPU_MANUAL_MODE.value, 0):
            self.cpuFanMode = PFS.Manual
            self.cpu_manual.setChecked(True)
        else:
            print("Warning: Unknow CPU fan mode value '" + self.cpuMode + "'")
            # self.cpuauto()
        
        if self.gpuMode == int(ECS.GPU_AUTO_MODE.value, 0) or self.gpuMode == int('0x00', 0):
            self.gpuFanMode = PFS.Auto
            self.gpu_auto.setChecked(True)
        elif self.gpuMode == int(ECS.GPU_TURBO_MODE.value, 0):
            self.gpuFanMode = PFS.Turbo
            self.gpu_turbo.setChecked(True)
        elif self.gpuMode == int(ECS.GPU_MANUAL_MODE.value, 0):
            self.gpuFanMode = PFS.Manual
            self.gpu_manual.setChecked(True)
        else:
            print("Warning: Unknow GPU fan mode value '" + str(self.gpuMode) + "'")
            # self.gpuauto()

        # if cpuTurboEnabled and gpuTurboEnabled:
        if self.turboEnabled:
            self.global_turbo.setChecked(True)
            self.cpu_turbo.setChecked(True)
            self.gpu_turbo.setChecked(True)
            self.predatorMode = int(ECS.TURBOMODE.value, 0) 
            self.setTurboMode()

    # Create a timer to update the UI
    def setUpdateUITimer(self):
        # print("Setting up timer...")
        self.my_timer = QTimer()
        self.my_timer.timeout.connect(self.updatePredatorStatus)
        self.my_timer.start(1000) #1 sec intervall        

    ## ----------------------------------------------------
    ## Read the various EC registers and update the GUI
    def checkPredatorStatus(self):
        # self.cb = self.ECHandler.ec_read(int(COOL_BOOST_CONTROL, 0)) == 1
        self.cpuMode = self.ECHandler.ec_read(int(ECS.CPU_FAN_MODE_CONTROL.value, 0))
        self.gpuMode = self.ECHandler.ec_read(int(ECS.GPU_FAN_MODE_CONTROL.value, 0))
        self.KB30Timeout = self.ECHandler.ec_read(int(ECS.KB_30_SEC_AUTO.value, 0))
        self.usbCharging = self.ECHandler.ec_read(int(ECS.POWEROFFUSBCHARGING.value, 0))
        self.displayOverdrive = self.ECHandler.ec_read(int(ECS.LCDOVERDRIVE.value, 0))
        self.predatorMode = self.ECHandler.ec_read(int(ECS.PREDATORMODE.value, 0))
        self.batteryChargeLimit = self.ECHandler.ec_read(int(ECS.BATTERYCHARGELIMIT.value, 0))
        self.trackpad = self.ECHandler.ec_read(int(ECS.TRACKPADSTATUS.value, 0))

        self.cpuFanSpeed = self.ECHandler.ec_read(int(ECS.CPU_MANUAL_SPEED_CONTROL.value, 0))
        self.gpuFanSpeed = self.ECHandler.ec_read(int(ECS.GPU_MANUAL_SPEED_CONTROL.value, 0))
        self.cpuManualSlider.setSliderPosition(int(self.cpuFanSpeed / 10))
        self.gpuManualSlider.setSliderPosition(int(self.gpuFanSpeed / 10))

    ## ----------------------------------------------------
    ## Read the newest register updates
    def checkPowerTempFan(self):
        ## Refresh the EC registers first before reading values
        # -optimisation, read EC registers once per update, prevents hangs/unresponsive GUI 
        self.ECHandler.ec_refresh()

        self.cpuMode = self.ECHandler.ec_read(int(ECS.CPU_FAN_MODE_CONTROL.value, 0))
        self.gpuMode = self.ECHandler.ec_read(int(ECS.GPU_FAN_MODE_CONTROL.value, 0))
        self.powerPluggedIn = self.ECHandler.ec_read(int(ECS.POWERSTATUS.value, 0))
        self.onBatteryPower = self.ECHandler.ec_read(int(ECS.BATTERYSTATUS.value, 0))
        self.predatorMode = self.ECHandler.ec_read(int(ECS.PREDATORMODE.value, 0))

        self.cpuTemp = self.ECHandler.ec_read(int(ECS.CPUTEMP.value, 0))
        self.gpuTemp = self.ECHandler.ec_read(int(ECS.GPUTEMP.value, 0))
        self.sysTemp = self.ECHandler.ec_read(int(ECS.SYSTEMP.value, 0))

        cpufanspeedHighBits = self.ECHandler.ec_read(int(ECS.CPUFANSPEEDHIGHBITS.value, 0))
        cpufanspeedLowBits = self.ECHandler.ec_read(int(ECS.CPUFANSPEEDLOWBITS.value, 0))
        ## example
        # cpufanspeed = '0x068B'
        # 1675
        self.cpufanspeed = cpufanspeedLowBits << 8 | cpufanspeedHighBits

        gpufanspeedHighBits = self.ECHandler.ec_read(int(ECS.GPUFANSPEEDHIGHBITS.value, 0))
        gpufanspeedLowBits = self.ECHandler.ec_read(int(ECS.GPUFANSPEEDLOWBITS.value, 0))
        self.gpufanspeed = gpufanspeedLowBits << 8 | gpufanspeedHighBits
        # print("cpufanspeed: " + str(cpufanspeed))
        # print("gpufanspeed: " + gpufanspeed)

    ## ---------Radio Button callback functions------------
    def setQuietMode(self):
        self.ECHandler.ec_write(int(ECS.PREDATORMODE.value, 0), int(ECS.QUIETMODE.value, 0))
        self.setGlobalAuto()

    def setDefaultMode(self):
        self.ECHandler.ec_write(int(ECS.PREDATORMODE.value, 0), int(ECS.DEFAULTMODE.value, 0))
        self.setGlobalAuto() 

    def setExtremeMode(self):
        self.ECHandler.ec_write(int(ECS.PREDATORMODE.value, 0), int(ECS.EXTREMEMODE.value, 0))
        self.setGlobalAuto()

    def setTurboMode(self):
        self.ECHandler.ec_write(int(ECS.PREDATORMODE.value, 0), int(ECS.TURBOMODE.value, 0))
        self.setGlobalTurbo()

    def setGlobalAuto(self):
        if self.turboEnabled:
            self.turboEnabled = False

            self.cpuauto()
            self.gpuauto()

            self.global_auto.setChecked(True)
            self.cpu_auto.setChecked(True)
            self.gpu_auto.setChecked(True)

    def setGlobalTurbo(self):
        if not self.turboEnabled:        
            self.turboEnabled = True

            self.cpumax()
            self.gpumax()

            self.global_turbo.setChecked(True)
            self.cpu_turbo.setChecked(True)
            self.gpu_turbo.setChecked(True)

    def cpuauto(self):
        self.ECHandler.ec_write(int(ECS.CPU_FAN_MODE_CONTROL.value, 0), int(ECS.CPU_AUTO_MODE.value, 0))
        self.cpuFanMode = PFS.Auto
        self.ledset()

    def cpumax(self):
        self.ECHandler.ec_write(int(ECS.CPU_FAN_MODE_CONTROL.value, 0), int(ECS.CPU_TURBO_MODE.value, 0))
        self.cpuFanMode = PFS.Turbo
        self.ledset()

    def cpusetmanual(self):
        self.ECHandler.ec_write(int(ECS.CPU_FAN_MODE_CONTROL.value, 0), int(ECS.CPU_MANUAL_MODE.value, 0))
        self.cpuFanMode = PFS.Manual

    def cpumanual(self, level):
        # print(str(level * 10), end=', ')
        # print(hex(level * 10))
        self.ECHandler.ec_write(int(ECS.CPU_MANUAL_SPEED_CONTROL.value, 0), level * 10)        

    def gpuauto(self):
        self.ECHandler.ec_write(int(ECS.GPU_FAN_MODE_CONTROL.value, 0), int(ECS.GPU_AUTO_MODE.value, 0))
        self.gpuFanMode = PFS.Auto

    def gpumax(self):
        self.ECHandler.ec_write(int(ECS.GPU_FAN_MODE_CONTROL.value, 0), int(ECS.GPU_TURBO_MODE.value, 0))
        self.gpuFanMode = PFS.Turbo

    def gpusetmanual(self):
        self.ECHandler.ec_write(int(ECS.GPU_FAN_MODE_CONTROL.value, 0), int(ECS.GPU_MANUAL_MODE.value, 0))
        self.gpuFanMode = PFS.Manual        

    def gpumanual(self, level):
        # print(level * 10, end=', ')
        # print(hex(level * 10))
        self.ECHandler.ec_write(int(ECS.GPU_MANUAL_SPEED_CONTROL.value, 0), level * 10)

    ## Toggle coolboost register
    # def toggleCB(self, tog):
    #     print('CoolBoost Toggle: ', end='')
    #     if tog:
    #         print('On')
    #         self.ECHandler.ec_write(int(COOL_BOOST_CONTROL, 0), int(COOL_BOOST_ON, 0))
    #     else:
    #         print('Off')
    #         self.ECHandler.ec_write(int(COOL_BOOST_CONTROL, 0), int(COOL_BOOST_OFF, 0))

    # Toggle 30 seconds keyboard backlight timer
    def togglekbauto(self, tog):
        if not tog:
            self.ECHandler.ec_write(int(ECS.KB_30_SEC_AUTO.value, 0), int(ECS.KB_30_AUTO_OFF.value, 0))
        else:
            self.ECHandler.ec_write(int(ECS.KB_30_SEC_AUTO.value, 0), int(ECS.KB_30_AUTO_ON.value, 0))

    # Toggle LCD Overdrive
    def toggleLCDOverdrive(self, tog):
        if tog:
            self.displayOverdrive = self.ECHandler.ec_read(int(ECS.LCDOVERDRIVE.value, 0))
            displayOverdriveMask = self.displayOverdrive + (1 << 3)
            self.ECHandler.ec_write(int(ECS.LCDOVERDRIVE.value, 0), displayOverdriveMask)
        else:
            displayOverdriveMask = self.displayOverdrive - (1 << 3)
            self.ECHandler.ec_write(int(ECS.LCDOVERDRIVE.value, 0), displayOverdriveMask)
    
    # USB charging whilst off
    def toggleUSBCharging(self, tog):
        if tog:
            self.ECHandler.ec_write(int(ECS.POWEROFFUSBCHARGING.value, 0), int(ECS.USBCHARGINGON.value, 0))
        else:
            self.ECHandler.ec_write(int(ECS.POWEROFFUSBCHARGING.value, 0), int(ECS.USBCHARGINGOFF.value, 0))

    ## We can toggle the register but it does nothing to actually disble the trackpad
    # def toggletrackpad(self, tog):
    #     if not tog:
    #         self.ECHandler.ec_write(int(ECS.TRACKPADSTATUS.value, 0), int(ECS.TRACKPADENABLED.value, 0))
    #     else:
    #         self.ECHandler.ec_write(int(ECS.TRACKPADSTATUS.value, 0), int(ECS.TRACKPADDISABLED.value, 0))

    ## ----------------------------------------------------
    # Toggle the Turbo Led
    def ledset(self):
        turboLedEnabled = self.ECHandler.ec_read(int(ECS.TURBO_LED_CONTROL.value, 0)) == int(ECS.TURBO_LED_ON.value, 0)
        if self.turboEnabled:
            if not turboLedEnabled:
                self.ECHandler.ec_write(int(ECS.TURBO_LED_CONTROL.value, 0), int(ECS.TURBO_LED_ON.value, 0))     
        else:
            if turboLedEnabled:
                self.ECHandler.ec_write(int(ECS.TURBO_LED_CONTROL.value, 0), int(ECS.TURBO_LED_OFF.value, 0))         

    # Update the Battery status
    def setBatteryStatus(self):
        batteryStat = 'Discharging'
        if self.onBatteryPower == int(ECS.BATTERYPLUGGEDINANDCHARGING.value, 0):
            batteryStat = "Charging"
        elif self.onBatteryPower == int(ECS.BATTERYDRAINING.value, 0):
            batteryStat = "Discharging"
        elif self.onBatteryPower == int(ECS.BATTERYOFF.value, 0):
            batteryStat = "Battery Not In Use"
        else:
            print("Error read EC register for Battery Status: " + str(self.predatorMode))

        self.batteryStatusValue.setText(batteryStat)

    # Update the Predator state
    def setPredatorMode(self):
        # print("predatorModeValue: " + str(self.predatorMode))
        if self.predatorMode == int(ECS.QUIETMODE.value, 0):
            self.predatorModeValue.setText("Quiet\t")
            self.quietModeCB.setChecked(True)
        elif self.predatorMode == int(ECS.DEFAULTMODE.value, 0):
            self.predatorModeValue.setText("Default\t")
            self.defaultModeCB.setChecked(True)
        elif self.predatorMode == int(ECS.EXTREMEMODE.value, 0):
            self.predatorModeValue.setText("Extreme\t")
            self.extremeModeCB.setChecked(True)
        elif self.predatorMode == int(ECS.TURBOMODE.value, 0):
            self.predatorModeValue.setText("Turbo\t")
            self.turboModeCB.setChecked(True)
        else:
            print("Error read EC register for Predator Mode: " + str(self.predatorMode))

        # self.predatorModeValue.adjustSize()

    # Update the UI state
    def updatePredatorStatus(self):
        checkVoltage(self)
        self.checkPowerTempFan()

        # print(self.cpuMode)
        # print(self.gpuMode)
        # print(int(ECS.CPU_TURBO_MODE.value, 0))
        # print(int(ECS.GPU_TURBO_MODE.value, 0))
        # print("-----------")

        if (self.cpuMode == int(ECS.CPU_TURBO_MODE.value, 0) or self.cpuMode == int('0xA8', 0)) and self.gpuMode == int(ECS.GPU_TURBO_MODE.value, 0):
            if not self.turboEnabled:
                print("Turbo enabled")
                self.setTurboMode()

        if self.cpuMode == int(ECS.CPU_AUTO_MODE.value, 0) and self.gpuMode == int(ECS.GPU_AUTO_MODE.value, 0):
            if self.turboEnabled:
                print("Turbo disabled")
                self.setDefaultMode()
           
        self.setBatteryStatus()
        self.setPredatorMode()

        # print("Sensors: %s, %s, %s, %s, %s, %s, %s" % (str(self.cpufanspeed), str(self.gpufanspeed), 
        #     str(self.cpuTemp), str(self.gpuTemp), str(self.sysTemp), str(self.powerPluggedIn), str(batteryStat)))

        self.cpuFanSpeedValue.setText(str(self.cpufanspeed) + " RPM")
        self.gpuFanSpeedValue.setText(str(self.gpufanspeed) + " RPM")
        self.cpuTempValue.setText(str(self.cpuTemp) + "°")
        self.gpuTempValue.setText(str(self.gpuTemp) + "°")
        self.sysTempValue.setText(str(self.sysTemp) + "°")

        self.powerStatusValue.setText(str(self.powerPluggedIn))

        # self.updateUI(Ui_PredatorSense, str(self.cpufanspeed), str(self.gpufanspeed),
        #     str(self.cpuTemp), str(self.gpuTemp), str(self.sysTemp), str(self.powerPluggedIn), str(batteryStat))        

    ## ----------------------------------------------------
    # Exit the program cleanly
    def shutdown(self):
        self.ECHandler.shutdownEC()
        print("Exiting")
        exit()

app = QtWidgets.QApplication(sys.argv)
application = MainWindow()
app.setApplicationName("Linux PredatorSense")
application.setFixedSize(application.WIDTH, application.HEIGHT) # Makes the window not resizeable
application.setWindowIcon(QtGui.QIcon('app_icon.ico'))

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

application.show()
sys.exit(app.exec())
