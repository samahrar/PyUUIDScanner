from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
from pylayout import Ui_BLEScanner
import bleak
import sys
from qasync import asyncSlot, asyncClose
from datetime import datetime
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# Work around for error: QWindowsContext: OleInitialize() failed:  "COM error 0xffffffff80010106 RPC_E_CHANGED_MODE (Unknown error 0x080010106)"
# Per: https://github.com/hbldh/bleak/issues/580#issuecomment-867928327
try:
    from winrt import _winrt
    _winrt.uninit_apartment()
except ModuleNotFoundError as e:
    pass

class BleScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version="0.1"

        self.ui = Ui_BLEScanner()
        self.ui.setupUi(self)

        # scanner state
        self.scanner = None
        # Exit button
        self.ui.exitButton.clicked.connect(self.exit_app)
        # Start Button
        self.ui.startButton.clicked.connect(self.start_scan)
        # Stop Button
        self.ui.stopButton.clicked.connect(self.stop_scan)
        # Clear Button
        self.ui.clearButton.clicked.connect(self.clear_screen)
        
    async def ble_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        # Scanner call-back
        uuid = self.ui.uudiLine.text()
        if advertisement_data.service_uuids and uuid:
            if advertisement_data.service_uuids[0].upper() == uuid.upper():
                res = self.create_adv_string(advertisement_data)
                self.ui.textBox.append(res)
        elif advertisement_data.service_uuids:
            res = self.create_adv_string(advertisement_data)
            self.ui.textBox.append(res)


    def create_adv_string(self, advertisement_data: AdvertisementData):
        time_stamp = str(datetime.now().strftime('%H:%M:%S'))
        res = f"[{time_stamp}] - "
        if advertisement_data.local_name:
            res += f"local_name: {advertisement_data.local_name}, "
        if advertisement_data.manufacturer_data:
            res += f"Manufacurer_data: {advertisement_data.manufacturer_data}, "
        if advertisement_data.service_data:
            res += f"service_data: {advertisement_data.service_data}, "
        if advertisement_data.service_uuids:
            res += f"service_uuids: {advertisement_data.service_uuids} "
        return res

    @asyncClose
    async def exit_app(self,event):
        sys.exit()
    
    @asyncSlot()
    async def start_scan(self):
        # Start Scan
        uuid = self.ui.uudiLine.text()
        self.scanner =  bleak.BleakScanner()
        self.scanner.register_detection_callback(self.ble_callback)
        self.ui.label.setText(QtCore.QCoreApplication.translate("BLEScanner", "Scan Running"))
        self.ui.label.setStyleSheet("color : green;")
        await self.scanner.start()
        
        
    @asyncSlot()
    async def stop_scan(self):
        # Stop Scan
        if self.scanner:
            await self.scanner.stop()
            self.scanner = None
            self.ui.label.setText(QtCore.QCoreApplication.translate("BLEScanner", "Scan Stopped"))
            self.ui.label.setStyleSheet("color : red;")

    @asyncSlot()
    async def clear_screen(self):
        # Clear textBox
        self.ui.textBox.clear()
    