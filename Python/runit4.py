#!/usr/bin/python3

# Command to run GUI from in daemon screen:
# screen -dmS hydra bash -c "DISPLAY=:0 /home/pi/HydraBot/runit4.py"

"""
OpenCV Camera Properties for current camera
CAP_PROP_CONTRAST: 0.5
CAP_PROP_FORMAT: 16.0
CAP_PROP_SATURATION: 0.8203125
CAP_PROP_EXPOSURE: 0.0
CAP_PROP_BUFFERSIZE: 4.0
CAP_PROP_BACKEND: 200.0
CAP_PROP_TEMPERATURE: 4600.0
CAP_PROP_FRAME_HEIGHT: 480.0
CAP_PROP_GAIN: 0.0
CAP_PROP_GAMMA: 100.0
CAP_PROP_FRAME_WIDTH: 640.0
CAP_PROP_BACKLIGHT: 1.0
CAP_PROP_FOURCC: 1448695129.0
CAP_PROP_FPS: 30.0
CAP_PROP_AUTO_EXPOSURE: 0.75
CAP_PROP_SHARPNESS: 3.0
CAP_PROP_BRIGHTNESS: 0.5
CAP_PROP_AUTO_WB: 1.0
CAP_PROP_HUE: 0.5
CAP_PROP_MODE: 1448695129.0
CAP_PROP_CONVERT_RGB: 1.0
CAP_PROP_WB_TEMPERATURE: 4600.0


writeable props with prop number, min, default, and max values

CAP_PROP_FRAME_WIDTH: (3, 640.0, 640.0, 640.0)
CAP_PROP_FRAME_HEIGHT: (4, 480.0, 480.0, 480.0)
CAP_PROP_FPS: (5, 30.0, 30.0, 30.0)
CAP_PROP_BRIGHTNESS: (10, 0.0, 0.5, 1.0)
CAP_PROP_CONTRAST: (11, 0.0, 0.5, 1.0)
CAP_PROP_SATURATION: (12, 0.0, 0.8203125, 1.0)
CAP_PROP_HUE: (13, 0.0, 0.5, 1.0)
CAP_PROP_GAIN: (14, 0.0, 0.0, 1.0)
CAP_PROP_EXPOSURE: (15, 0.0, 0.0, 1.0)
CAP_PROP_CONVERT_RGB: (16, 0.0, 1.0, 1.0)
CAP_PROP_SHARPNESS: (20, 0.0, 3.0, 6.0)
CAP_PROP_AUTO_EXPOSURE: (21, 0.25, 0.75, 0.75)
CAP_PROP_GAMMA: (22, 72.0, 100.0, 500.0)
CAP_PROP_BACKLIGHT: (32, 0.0, 1.0, 2.0)
CAP_PROP_BUFFERSIZE: (38, 1.0, 4.0, 10.0)
CAP_PROP_AUTO_WB: (44, 0.0, 1.0, 1.0)

"""

# always seem to need this
import sys
import os
from time import perf_counter, sleep, time
import cv2
from numpy import ndarray, array
from pyzbar.pyzbar import ZBarSymbol
from pyzbar import pyzbar
import qrcode
from PIL.ImageQt import ImageQt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# os.environ['DISPLAY'] = '0'

# This gets the Qt stuff
# import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt, QSize, QObject, QCoreApplication

# This is our window from QtCreator
import hydragui
import media  # resource file prefix - :/HydraBot/media/

"""
camprops dict format - key = property enumeration, item = propID, min, default, max, page-step, step-factor, writable
"""
camprops = {}
#  Spinel IR Camera settings:
# camprops = {
#     'CAP_PROP_FRAME_WIDTH': 	(3,		640,	640,	2592,	1,	1,  1),
#     'CAP_PROP_FRAME_HEIGHT': 	(4,		480,	480,	1944,	1,	1,  1),  # Set Height to set width, drops to smaller resolution
#     'CAP_PROP_BRIGHTNESS': 		(10,	0,		8,		15,		1,	1,  1),
#     'CAP_PROP_CONTRAST': 		(11,	0,		8,		15,		1,	1,  1),
#     'CAP_PROP_SATURATION': 		(12,	0,		7,		15,		1,	1,  1),
#     'CAP_PROP_HUE': 			(13,	-10,	0,		10,		1,	1,  1),
#     'CAP_PROP_GAIN': 			(14,	0,		0,		0,		1,	1,  0),
#     'CAP_PROP_EXPOSURE': 		(15,	-11,	-4,		-1,		1,	1,  1),
#     'CAP_PROP_CONVERT_RGB': 	(16,	0,		1,		1,		1,	1,  1),
#     'CAP_PROP_SHARPNESS': 		(20,	0,		6,		15,		1,	1,  1),
#     'CAP_PROP_AUTO_EXPOSURE': 	(21,	0,		1,		1,		1,	1,  1),
#     'CAP_PROP_GAMMA': 			(22,	1,		7,		9,		1,	1,  1),
#     'CAP_PROP_TEMPERATURE': 	(23,	2800,	2800,	6500,	1,	1,  1),
#     'CAP_PROP_FOCUS': 			(28,	0,		16,		21,		1,	1,  1),
#     'CAP_PROP_AUTOFOCUS': 		(39,	0,		1,		1,		1,	1,  1),
# }

#  Spinel Aptina 5MP settings:
#  MSMF
MSMF = {
    'CAP_PROP_FRAME_WIDTH':		(3,		640,	640,	2592,	1,	1,	1),
    'CAP_PROP_FRAME_HEIGHT':	(4,		480,	480,	1944,	1,	1,	1),
    'CAP_PROP_BRIGHTNESS':		(10,	0,		0,		64,		4,	1,	1),
    'CAP_PROP_CONTRAST':		(11,	0,		32,		64,		4,	1,	1),
    'CAP_PROP_SATURATION':		(12,	0,		64,		128,	8,	1,	1),
    'CAP_PROP_HUE':				(13,	-40,	0,		40,		4,	1,	1),
    'CAP_PROP_GAIN':			(14,	0,		0,		100,	10,	1,	1),
    'CAP_PROP_EXPOSURE':		(15,	-13,	-6,		-1,		1,	1,	1),
    'CAP_PROP_SHARPNESS':		(20,	0,		3,		6,		1,	1,	1),
    'CAP_PROP_AUTO_EXPOSURE':	(21,	0,		1,		1,		1,	1,	1),
    'CAP_PROP_GAMMA':			(22,	72,		100,	500,	14,	1,	1)
}

V4L2 = {
    'CAP_PROP_FRAME_WIDTH':		(3,		640,	640,	2592,	1,	1,	    1),
    'CAP_PROP_FRAME_HEIGHT':	(4,		480,	480,	1944,	1,	1,	    1),
    'CAP_PROP_BRIGHTNESS':		(10,	0,		0.5,	1,		10,	1000,	1),
    'CAP_PROP_CONTRAST':		(11,	0,		0.5,	1,		10,	1000,   1),
    'CAP_PROP_SATURATION':		(12,	0,		0.5,	1,  	10,	1000,   1),
    'CAP_PROP_HUE':				(13,	0,  	0.5,	1,		10,	1000,   1),
    'CAP_PROP_GAIN':			(14,	0,		0,		1,	    10,	1000,   1),
    'CAP_PROP_EXPOSURE':		(15,	0,  	0.1,	1,		10,	1000,   1),
    'CAP_PROP_SHARPNESS':		(20,	0,		3,		6,		1,	1,	    1),
    'CAP_PROP_AUTO_EXPOSURE':	(21,	0.25,	0.75,	0.75,	1,	1,	    1),
    'CAP_PROP_GAMMA':			(22,	72,		100,	500,	14,	1,	    1)
}

# Original HydraBot camera settings
# camprops = {
#     'CAP_PROP_FRAME_WIDTH': 	(3,		640,	640,	2592,	1,	1,      1),
#     'CAP_PROP_FRAME_HEIGHT': 	(4,		480,	480,	1944,	1,	1,      1),  # Set Height to set width, drops to smaller resolution
#     'CAP_PROP_BRIGHTNESS': 		(10,	0,		0.5,	1,		10,	1000,   1),
#     'CAP_PROP_CONTRAST': 		(11,	0,		0.5,	1,		10,	1000,   1),
#     'CAP_PROP_SATURATION': 		(12,	0,		0.82,	1,		10,	1000,   1),
#     'CAP_PROP_HUE': 			(13,	0,  	0.5,	1,		10,	1000,   1),
#     'CAP_PROP_GAIN': 			(14,	0,		0,		1,		10,	1000,   1),
#     'CAP_PROP_EXPOSURE': 		(15,	0,  	0,		1,		10,	1000,   1),
#     'CAP_PROP_CONVERT_RGB': 	(16,	0,		1,		1,		1,	1,      1),
#     'CAP_PROP_SHARPNESS': 		(20,	0,		3,		6,		1,	1,      1),
#     'CAP_PROP_AUTO_EXPOSURE': 	(21,	0.25,	0.75,	0.75,	1,	1,      1),
#     'CAP_PROP_GAMMA': 			(22,	72,		100,	500,	42,	1,      1),
#     'CAP_PROP_TEMPERATURE': 	(23,	2800,	2800,	6500,	1,	1,      0),
#     'CAP_PROP_FOCUS': 			(28,	0,		16,		21,		1,	1,      0),
#     'CAP_PROP_AUTOFOCUS': 		(39,	0,		1,		1,		1,	1,      0),
# }

sliders = {
    'exposureSlider': [15, None, 1],
    'gainSlider': [14, None, 1],
    'gammaSlider': [22, None, 1],
    'hueSlider': [13, None, 1],
    'contrastSlider': [11, None, 1],
    'saturationSlider': [12, None, 1],
    'sharpnessSlider': [20, None, 1],
}


#
# sliders = {
#     'exposureSlider': [15, None, 1000],
#     'gainSlider': [14, None, 1000],
#     'gammaSlider': [22, None, 1],
#     'hueSlider': [13, None, 1000],
#     'contrastSlider': [11, None, 1000],
#     'saturationSlider': [12, None, 1000],
#     'sharpnessSlider': [20, None, 1],
# }


class CamWorker(QObject):

    newFrame = pyqtSignal(ndarray)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.stopNow = False

    @pyqtSlot()
    def stopCam(self):
        self.stopNow = True

    @pyqtSlot(cv2.VideoCapture)
    def startCam(self, cam):
        while self.stopNow is False and cam.isOpened() is True:
            check = cam.grab()
            QThread.yieldCurrentThread()
            QCoreApplication.processEvents()
            try:
                if check is True and cam.isOpened() is True and self.stopNow is False:
                    check, frame = cam.retrieve()
                    if check is True:
                        self.newFrame.emit(frame)
                        QThread.yieldCurrentThread()
            except:
                QCoreApplication.processEvents()
                continue
        if cam.isOpened() is True:
            cam.release()
        print('Camera Released')


class ZbarWorker(QObject):

    showCode = pyqtSignal(ndarray)
    newScans = pyqtSignal(dict)
    qrReady = pyqtSignal()

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    @pyqtSlot(ndarray, dict)
    def decodeQR(self, frame, qrlist):
        now = time()
        yNew = round(frame.shape[0] / 2)
        xNew = round(frame.shape[1] / 2)
        barcodes = pyzbar.decode(cv2.resize(frame, (xNew, yNew)), symbols=[ZBarSymbol.QRCODE])
        QThread.yieldCurrentThread()
        if len(barcodes) > 0:
            update = False
            for barcode in barcodes:
                bData = barcode.data.decode('utf-8')
                if bData in qrlist.keys():
                    if now - qrlist[bData] < 1:
                        continue
                qrlist[bData] = now
                (x, y, w, h) = barcode.rect
                (x, y, w, h) = (x * 2, y * 2, w * 2, h * 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, bData, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                update = True
            if update is True:
                self.showCode.emit(frame)
            toRemove = []
            for code, then in qrlist.items():
                if now - then > 300:
                    toRemove.append(code)
            for code in toRemove:
                del (qrlist[code])
            self.newScans.emit(qrlist)
        self.qrReady.emit()


# create class for our Raspberry Pi GUI
class MainWindow(QMainWindow, hydragui.Ui_MainWindow):
    # access variables inside of the UI's file

    camStartSignal = pyqtSignal(cv2.VideoCapture, name='camStartSignal')
    camStopSignal = pyqtSignal(name='camStopSignal')
    decodeQrSignal = pyqtSignal(ndarray, dict, name='decodeQrSignal')

    def setImage(self, image):
        if image is None:
            return
        self.rgbImg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if self.qr_ready is True:
            self.decodeQrSignal.emit(self.rgbImg, self.codeList)
        if self.doPreview is False:
            return
        shape = self.rgbImg.shape
        if self.cam_width is None or self.cam_width != shape[1]:
            self.cam_height, self.cam_width, channel = self.rgbImg.shape
            self.cam_bytes_per_line = 3 * self.cam_width
            print((self.cam_width, self.cam_height))
        pMap = QPixmap.fromImage(
            QImage(self.rgbImg.data, self.cam_width, self.cam_height, self.cam_bytes_per_line, QImage.Format_RGB888)
        )
        self.CamPreviewLabel.setPixmap(pMap.scaled(self.cam_preview_width, self.cam_preview_height, Qt.KeepAspectRatio))

    def procImage(self, image=None):
        if image is None:
            if self.rgbImg is None:
                return
            image = self.rgbImg
        # cv2.imshow('HydraBotImage', cv2.cvtColor(self.rgbImg, cv2.COLOR_RGB2BGR))
        # cv2.waitKey(1)
        pMap = QPixmap.fromImage(
            QImage(image.data, self.cam_width, self.cam_height, self.cam_bytes_per_line, QImage.Format_RGB888)
        )
        s = self.SnapLabel.size()
        self.SnapLabel.setPixmap(pMap.scaled(s.width(), s.height(), Qt.KeepAspectRatio))

    def createQR(self, qrdata=None, savename=None):
        #  savename must contain the full path and extension to properly save the QR code, saves as PNG
        if qrdata is None or qrdata is False:
            qrdata = self.plateIDLineEdit.text()
            if len(qrdata) == 0:
                qrdata = 'Hydra~XXX-20201231001'
            savename = os.path.join(os.getcwd(), 'tempQR.png')
            print(savename)
        else:
            print('qrdata passed')
            print(qrdata)
        pilqr = qrcode.make(qrdata)
        self.qrData = qrdata
        # cvqr = array(pilqr.convert('RGB'))  # This line converts to OpenCV image
        if savename is not None and savename is not False:
            try:
                pilqr.save(savename, 'PNG')
                print('QR Code saved to: ' + savename)
                self.qrFile = savename
            except:
                print('QR Code save failed to path: ' + str(savename))
        self.QRDispLabel.setPixmap(QPixmap.fromImage(ImageQt(pilqr)))

    def updateScans(self, qrlist):
        self.scans += len(qrlist)
        self.scansLabel.setText(str(self.scans))
        self.codeList = qrlist

    def emailQR(self):
        address = self.emailLineEdit.text()
        password = self.passLineEdit.text()
        smtpAddr = self.SMTPLineEdit.text()
        if len(smtpAddr) == 0:
            smtpAddr = 'smtp.gmail.com'
        try:
            server = smtplib.SMTP(smtpAddr, 587)
            server.starttls()
            server.login(address, password)
        except Exception as e:
            print(e)
            print('Could not log into SMTP server, check that your account is set to allow SMTP connections: ' + smtpAddr)
            return
        recipient = self.emailToLineEdit.text()
        msg = MIMEMultipart()
        msg['From'] = address
        msg['To'] = recipient
        msg['Subject'] = 'HydraBot New Plate QR Code: ' + self.qrData
        body = 'Here is the new plate QR code that was generated.'
        msg.attach(MIMEText(body, 'plain'))
        if self.qrFile is not None:
            pic = open(self.qrFile, 'rb')
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(pic.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', 'attachment; filename=%s' % self.qrData + '.png')
            msg.attach(p)
        text = msg.as_string()
        server.sendmail(address, recipient, text)
        server.quit()

    def togglePreview(self):
        if self.previewCheckBox.isChecked():
            self.doPreview = True
        else:
            self.doPreview = False

    def genSetCamProp(self):
        prop = self.setPropEdit.text()
        prop = getattr(cv2, prop, -1)
        if prop == -1:
            self.setPropEdit.text('INVALID PROPERTY')
            return
        tmp = self.setValueEdit.text()
        try:
            val = float(tmp)
        except ValueError:
            val = tmp
        self.setCamProp(prop, val)

    def setCamProp(self, prop, val):
        if self.cam.set(prop, val):
            print('set ' + str(prop) + ' to ' + str(val) + ' successful')
            self.updateProps()
        else:
            print('set ' + str(prop) + ' to ' + str(val) + ' failed')

    def updateProps(self):
        val = self.cam.get(21)  # AUTO_EXPOSURE
        self.autoExpCheckBox.setChecked(val == self.autoexpOn)
        val = self.cam.get(15)  # EXPOSURE
        self.exposureSlider.setValue(round(val * self.expFactor))
        if self.expFactor > 1:
            val = round(val, 3)
        self.exposureValueLabel.setText(str(val))
        val = self.cam.get(14)  # GAIN
        self.gainSlider.setValue(round(val * self.gaiFactor))
        if self.gaiFactor > 1:
            val = round(val, 3)
        self.gainValueLabel.setText(str(val))
        val = self.cam.get(22)  # GAMMA
        self.gammaSlider.setValue(round(val * self.gamFactor))
        if self.gamFactor > 1:
            val = round(val, 3)
        self.gammaValueLabel.setText(str(val))
        val = self.cam.get(13)  # HUE
        self.hueSlider.setValue(round(val * self.hueFactor))
        if self.hueFactor > 1:
            val = round(val, 3)
        self.hueValueLabel.setText(str(val))
        val = self.cam.get(11)  # CONTRAST
        self.contrastSlider.setValue(round(val * self.conFactor))
        if self.conFactor > 1:
            val = round(val, 3)
        self.contrastValueLabel.setText(str(val))
        val = self.cam.get(12)  # SATURATION
        self.saturationSlider.setValue(round(val * self.satFactor))
        if self.satFactor > 1:
            val = round(val, 3)
        self.saturationValueLabel.setText(str(val))
        val = self.cam.get(20)  # SHARPNESS
        self.sharpnessSlider.setValue(round(val * self.shaFactor))
        if self.shaFactor > 1:
            val = round(val, 3)
        self.sharpnessValueLabel.setText(str(val))

    def genGetCamProp(self):
        prop = self.getPropEdit.text()
        prop = getattr(cv2, prop, -1)
        if prop == -1:
            self.getPropEdit.text('INVALID PROPERTY')
            return
        val = self.cam.get(prop)
        self.getOutputLabel.setText(str(val))

    def autoExpChanged(self):
        if self.autoExpCheckBox.isChecked():
            val = self.autoexpOn
        else:
            val = self.autoexpOff
        self.setCamProp(21, val)

    def sliderChanged(self):
        obj = self.sender()
        name = obj.objectName()
        info = sliders[name]
        val = obj.value() / info[2]
        info[1].setText(str(val))

    def sliderReleased(self):
        obj = self.sender()
        name = obj.objectName()
        info = sliders[name]
        val = obj.value() / info[2]
        info[1].setText(str(val))
        self.setCamProp(info[0], val)

    def qrReady(self):
        self.qr_ready = True

    def setupCamProps(self):
        vals = camprops['CAP_PROP_AUTO_EXPOSURE']
        self.autoexpOff = vals[1]
        self.autoexpOn = vals[3]

        slider = self.exposureSlider
        vals = camprops['CAP_PROP_EXPOSURE']
        self.expFactor = vals[5]
        sliders['exposureSlider'] = [15, self.exposureValueLabel, self.expFactor]
        self.setupSlider(slider, vals)

        slider = self.gainSlider
        vals = camprops['CAP_PROP_GAIN']
        self.gaiFactor = vals[5]
        sliders['gainSlider'] = [14, self.gainValueLabel, self.gaiFactor]
        self.setupSlider(slider, vals)

        slider = self.gammaSlider
        vals = camprops['CAP_PROP_GAMMA']
        self.gamFactor = vals[5]
        sliders['gammaSlider'] = [22, self.gammaValueLabel, self.gamFactor]
        self.setupSlider(slider, vals)

        slider = self.hueSlider
        vals = camprops['CAP_PROP_HUE']
        self.hueFactor = vals[5]
        sliders['hueSlider'] = [13, self.hueValueLabel, self.hueFactor]
        self.setupSlider(slider, vals)

        slider = self.contrastSlider
        vals = camprops['CAP_PROP_CONTRAST']
        self.conFactor = vals[5]
        sliders['contrastSlider'] = [11, self.contrastValueLabel, self.conFactor]
        self.setupSlider(slider, vals)

        slider = self.saturationSlider
        vals = camprops['CAP_PROP_SATURATION']
        self.satFactor = vals[5]
        sliders['saturationSlider'] = [12, self.saturationValueLabel, self.satFactor]
        self.setupSlider(slider, vals)

        slider = self.sharpnessSlider
        vals = camprops['CAP_PROP_SHARPNESS']
        self.shaFactor = vals[5]
        sliders['sharpnessSlider'] = [20, self.sharpnessValueLabel, self.shaFactor]
        self.setupSlider(slider, vals)

    def setupSlider(self, slider, vals):
        slider.setMinimum(vals[1] * vals[5])
        slider.setMaximum(vals[3] * vals[5])
        slider.setProperty("value", vals[2] * vals[5])
        slider.setSingleStep(1)
        slider.setPageStep(vals[4])
        if vals[6] == 0:
            slider.setEnabled(False)

    def createWidgets(self):
        self.exitToolButton = QToolButton()
        self.exitToolButton.setObjectName('exitToolButton')
        self.exitToolButton.setToolTip("Exit HydraBot")
        self.exitToolButton.setText("...")
        self.exitToolButton.setIcon(QIcon(QPixmap(':/HydraBot/media/Media/dialog_close.png')))
        self.exitToolButton.setIconSize(QSize(32, 32))
        self.statusbar.addPermanentWidget(self.exitToolButton)

    def connectSignals(self):
        self.sendEmailButton.clicked.connect(self.emailQR)
        self.previewCheckBox.clicked.connect(self.togglePreview)
        self.plateIDLineEdit.returnPressed.connect(self.createQR)
        self.createPlateButton.clicked.connect(self.createQR)
        self.setButton.clicked.connect(self.genSetCamProp)
        self.getButton.clicked.connect(self.genGetCamProp)
        self.autoExpCheckBox.clicked.connect(self.autoExpChanged)
        self.exposureSlider.valueChanged.connect(self.sliderChanged)
        self.exposureSlider.sliderReleased.connect(self.sliderReleased)
        self.gainSlider.valueChanged.connect(self.sliderChanged)
        self.gainSlider.sliderReleased.connect(self.sliderReleased)
        self.gammaSlider.valueChanged.connect(self.sliderChanged)
        self.gammaSlider.sliderReleased.connect(self.sliderReleased)
        self.hueSlider.valueChanged.connect(self.sliderChanged)
        self.hueSlider.sliderReleased.connect(self.sliderReleased)
        self.contrastSlider.valueChanged.connect(self.sliderChanged)
        self.contrastSlider.sliderReleased.connect(self.sliderReleased)
        self.saturationSlider.valueChanged.connect(self.sliderChanged)
        self.saturationSlider.sliderReleased.connect(self.sliderReleased)
        self.sharpnessSlider.valueChanged.connect(self.sliderChanged)
        self.sharpnessSlider.sliderReleased.connect(self.sliderReleased)
        self.CameraButton.clicked.connect(self.procImage)
        self.ExitButton.clicked.connect(self.cleanClose)
        self.exitToolButton.clicked.connect(self.cleanClose)

    def initCamera(self):
        self.cam = None
        self.cam_width = None
        self.cam_height = None
        self.cam_preview_width = 640
        self.cam_preview_height = 480
        self.cam_bytes_per_line = None
        self.rgbImg = None
        self.CamPreviewLabel.setFixedHeight(480)
        self.CamPreviewLabel.setFixedWidth(640)
        self.doPreview = True
        self.cam = cv2.VideoCapture(0)
        backend = self.cam.getBackendName()
        print(backend)
        if 'MSMF' in backend:
            camprops.update(MSMF)
        else:
            camprops.update(V4L2)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1921)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1081)
        self.setupCamProps()  # Load specific camera properties and apply to them to widgets
        self.camWorker = CamWorker()
        self.camThread = QThread()
        self.camWorker.moveToThread(self.camThread)
        self.camThread.start()
        self.camWorker.newFrame.connect(self.setImage)
        self.camStartSignal.connect(self.camWorker.startCam)
        self.camStopSignal.connect(self.camWorker.stopCam)
        self.updateProps()
        print('cam initialized')

    def initZbar(self):
        self.qrData = ''
        self.qrFile = None
        self.codeList = dict()
        self.scans = 0
        self.qrWorker = ZbarWorker()
        self.qrThread = QThread()
        self.qrWorker.moveToThread(self.qrThread)
        self.qrThread.start()
        self.qrWorker.newScans.connect(self.updateScans)
        self.qrWorker.showCode.connect(self.procImage)
        self.qrWorker.qrReady.connect(self.qrReady)
        self.decodeQrSignal.connect(self.qrWorker.decodeQR)
        self.qr_ready = True
        print('QR reader initialized')

    def cleanClose(self):
        print('Closing HydraBot')
        print('Stopping Camera Thread')
        self.camStopSignal.emit()
        QThread.msleep(50)
        self.camThread.quit()
        if self.camThread.wait(100) is False:
            print('Timed out waiting on Camera Thread')
        print('Waiting on QR Thread')
        while self.qr_ready is False:
            QThread.msleep(10)
        print('Stopping QR Thread')
        self.qrThread.quit()
        if self.qrThread.wait(1000) is False:
            print('Timed out waiting on QR Thread')
        print('Closed')
        self.close()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)  # gets defined in the UI file

        self.createWidgets()  # Create non-Creator widgets and set them up

        self.connectSignals()  # Make signal connections between widgets

        self.initCamera()  # Create camera and camera variables.  Make connections

        self.initZbar()  # Create QR code scanner and variables.  Make connections

        self.camStartSignal.emit(self.cam)

# I feel better having one of these
def main():
    # a new app instance
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    # without this, the script exits immediately.
    sys.exit(app.exec_())


# python bit to figure how who started This
if __name__ == "__main__":
    main()
