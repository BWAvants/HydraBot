#!/usr/bin/python3

# Command to run GUI from in daemon screen:
# screen -dmS hydra bash -c "DISPLAY=:0 /home/pi/hydrabot/hydrabot.py"

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
import logging
import sys
import os
import contextlib
from io import StringIO
import subprocess as subp
from subprocess import PIPE, STDOUT
from collections import OrderedDict
from time import perf_counter, sleep, time
import cv2
import socket
from select import select
from numpy import ndarray, array, uint16, uint8, around, zeros, ones
from pyzbar.pyzbar import ZBarSymbol
from pyzbar import pyzbar
import segno
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import hydradb
# This gets the Qt stuff
# import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont, QPainter, QBrush, QRadialGradient, QColor
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt, QSize, QObject, QCoreApplication, QTimer
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
# This is our window from QtCreator
import hydragui
# import media_rc  # resource file prefix - :/HydraBot/media/

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

# os.environ['DISPLAY'] = '0'

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

IMG_READ_FORMATS = ('BMP', 'GIF', 'JPG', 'JPEG', 'PNG', 'PBM', 'PGM', 'PPM', 'XBM', 'XPM')
IMG_WRITE_FORMATS = ('BMP', 'JPG', 'JPEG', 'PNG', 'PPM', 'XBM', 'XPM')

EXPOSURE_MODES = {QCameraExposure.ExposureAuto: 'Auto', QCameraExposure.ExposureManual: 'Manual',
                  QCameraExposure.ExposurePortrait: 'Portrait', QCameraExposure.ExposureNight: 'Night',
                  QCameraExposure.ExposureBacklight: 'Backlight', QCameraExposure.ExposureSpotlight: 'Spotlight',
                  QCameraExposure.ExposureSports: 'Sports', QCameraExposure.ExposureSnow: 'Snow',
                  QCameraExposure.ExposureBeach: 'Beach', QCameraExposure.ExposureLargeAperture: 'Large Aperture',
                  QCameraExposure.ExposureSmallAperture: 'Small Aperture', QCameraExposure.ExposureAction: 'Action',
                  QCameraExposure.ExposureLandscape: 'Landscape',
                  QCameraExposure.ExposureNightPortrait: 'Night Portrait', QCameraExposure.ExposureTheatre: 'Theatre',
                  QCameraExposure.ExposureSunset: 'Sunset', QCameraExposure.ExposureSteadyPhoto: 'Steady Photo',
                  QCameraExposure.ExposureFireworks: 'Fireworks', QCameraExposure.ExposureParty: 'Party',
                  QCameraExposure.ExposureCandlelight: 'Candle Light', QCameraExposure.ExposureBarcode: 'Barcode'}

SHUTTER_SPEEDS = [8192.0, 4096.0, 2048.0, 1024.0, 512.0, 256.0, 128.0, 64.0, 32.0, 16.0, 8.0, 4.0]

def check_image_format(filename, io='write'):
    if 'write' == io:
        formats = IMG_WRITE_FORMATS
    else:
        formats = IMG_READ_FORMATS
    ending = filename[-3:].upper()
    if ending in formats:
        encoding = ending
    else:
        ending = filename[-3:].upper()
        if ending in formats:
            encoding = ending
        else:
            filename = filename + '.png'
            encoding = 'PNG'
    return (filename, encoding)

@contextlib.contextmanager
def stdout_redirect(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def hydrabot_server_setup(host, reboot=True):
    server_filename = 'hydrabotserver.py.py'
    launcher_filename = 'hydrabotserver_start'  # filename CANNOT end in .sh even though it is a shell script
    args = ['ssh', '-o', 'StrictHostKeyChecking=no', 'root@%s' % host,
            'cat', '>',  '/data/user_storage/%s' % server_filename]
    try:
        with open(server_filename, 'rb') as f:
            uploader = subp.run(args, input=f.read(), timeout=3)
        uploader.check_returncode()
        print('Upload Successful ~ %s : /data/user_storage/%s' % (server_filename, server_filename))
    except OSError as e:
        print(e)
        return
    except subp.CalledProcessError as e:
        print(e)
        return
    args = ['ssh', '-o', 'StrictHostKeyChecking=no', 'root@%s' % host,
            'cat', '>', '/data/boot.d/%s' % launcher_filename]
    try:
        with open(launcher_filename, 'rb') as f:
            uploader = subp.run(args, input=f.read(), timeout=1)
        uploader.check_returncode()
        print('Upload Successful ~ %s : /data/boot.d/%s' % (launcher_filename, launcher_filename))
        out = subp.run(['ssh', 'root@%s' % host, 'chmod', '765', '/data/boot.d/%s' % launcher_filename], timeout=1)
        out.check_returncode()
        print('Launcher execution permissions set: 765')
    except OSError as e:
        print(e)
        return
    except subp.CalledProcessError as e:
        print(e)
        return
    if reboot:
        subp.run(['ssh', 'root@%s' % host, 'reboot'], timeout=1)


def hydrabot_connect(host, port=14400):
    #  This is a convenience function to allow users to interact with the server via static imported functions
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((host, port))
    return s


def hcom(s, cmd):
    #  This is a convenience function for communicating with the HydraBot server via static imported functions
    s.sendall(cmd.encode('utf-8'))
    resp = s.recv(4096)
    return resp.decode('utf-8')


class OT2Worker(QObject):

    ot2_connected = pyqtSignal(str)
    ot2_command_response = pyqtSignal(str)
    ot2_routine_done = pyqtSignal()
    ot2_new_event = pyqtSignal(QTreeWidgetItem)
    ot2_error = pyqtSignal(str)
    ot2_scan_qr = pyqtSignal()
    ot2_process_well = pyqtSignal()
    ot2_deck_scanned = pyqtSignal(dict)
    ot2_slot_update_signal = pyqtSignal(int, str, bool)

    def __init__(self, parent=None, host='8929b13.local', port=14400):
        super(self.__class__, self).__init__(parent)
        self.host = host
        self.port = port
        self.connection = None
        self.last_command = None
        self.last_response = None
        self.qr_scanned = None
        self.plates_on_deck = None
        self.well_processed = False


    @pyqtSlot(list)
    def qr_scanned_slot(self, scans):
        self.qr_scanned = scans

    @pyqtSlot()
    def qr_not_found_slot(self):
        self.qr_scanned = []

    @pyqtSlot()
    def well_processed_slot(self):
        self.well_processed = True

    @pyqtSlot(str)
    def cmd(self, missive):
        try:
            self.connection.sendall(missive.encode('utf-8'))
            t = time()
            while time() - t < 15:
                r, w, e = select([self.connection, ], [], [self.connection, ], .001)
                if len(r) > 0:
                    break
                if len(e) > 0:
                    self.ot2_error.emit('Socket connection error with HydraBot Server')
                    return
                QCoreApplication.processEvents()
                QThread.yieldCurrentThread()
            if time() - t > 15:
                self.ot2_error.emit('Socket connection timeout with HydraBot Server')
                return
            response = self.connection.recv(4096)
            if response:
                self.last_response = response.decode('utf-8')
                self.ot2_command_response.emit(self.last_response)
            else:
                self.ot2_error.emit('Server did not respond')
        except Exception as e:
            self.ot2_error.emit(str(e))

    @pyqtSlot()
    def connect(self):
        self._connect()

    @pyqtSlot(str, int)
    def _connect(self, host=None, port=None):
        if self.connection:
            print('Disconnect before connecting')
            self.ot2_error.emit('Attempted to connect while connection exists')
            return
        if host:
            self.host = host
        if port and port > 0:
            self.port = port
        try:
            print('Connecting to %s:%i' % (self.host, self.port))
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.connection.settimeout(0.5)
            self.connection.connect((self.host, self.port))
            version = self.connection.recv(1024).decode('utf-8')
            print(version)
            self.ot2_connected.emit(version)
        except Exception as e:
            self.ot2_error.emit(str(e))

    @pyqtSlot()
    def ot2_connect(self):
        if self.connection:
            self.cmd('robot.connect()')

    @pyqtSlot()
    def disconnect(self):
        try:
            if self.connection:
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
        except Exception as e:
            self.ot2_error.emit(str(e))
        finally:
            self.connection = None
            self.ot2_connected.emit('')

    @pyqtSlot()
    def home(self):
        self.cmd('robot.home()')

    @pyqtSlot()
    def home_z(self):
        self.cmd('robot.home_z()')

    @pyqtSlot(str, str, float)
    def cam_to(self, plate, well, height_offset):
        self.cmd("self.cam_to(self.%s, '%s', %f)" % (plate, well, height_offset))

    @pyqtSlot()
    def scan_plates(self):
        self._scan_plates()

    @pyqtSlot(list)
    def _scan_plates(self, plate_list=[3, 2, 1, 4, 5, 6, 9, 8, 7, 10]):
        self.plates_on_deck = dict()
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.ot2_scan_qr.emit)
        for plate in plate_list:
            # self.cmd('self.cam_to(self.plate_%i, "QR")' % plate)
            self.cam_to('plate_%s' % plate, 'QR', 0)
            self.ot2_slot_update_signal.emit(plate, None, True)
            self.qr_scanned = None
            timer.start(100)
            # QThread.msleep(150)
            # self.ot2_scan_qr.emit()
            t = time()
            while self.qr_scanned is None:
                QThread.yieldCurrentThread()
                QCoreApplication.processEvents()
                if time() - t > 3:
                    break
            if self.qr_scanned is not None and len(self.qr_scanned) > 0:
                self.plates_on_deck.update({self.qr_scanned[0]: plate})
                self.ot2_slot_update_signal.emit(plate, self.qr_scanned[0], False)
        self.ot2_deck_scanned.emit(self.plates_on_deck)
        if len(self.plates_on_deck) == 0:
            self.plates_on_deck = None


class CamWorker(QObject):

    newFrame = pyqtSignal(ndarray)
    camStopped = pyqtSignal()

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
            if check is True and cam.isOpened() is True and self.stopNow is False:
                check, frame = cam.retrieve()
                QThread.yieldCurrentThread()
                QCoreApplication.processEvents()
                if check is True and self.stopNow is False:
                    self.newFrame.emit(frame)
                    QThread.yieldCurrentThread()
                    QCoreApplication.processEvents()
        if cam.isOpened() is True:
            cam.release()
        print('Camera Released')
        self.camStopped.emit()


class CV2Worker(QObject):
    show_cv2 = pyqtSignal(QPixmap)
    cv2_info = pyqtSignal(dict)
    cv2_ready = pyqtSignal()

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.frame = None
        self.well = None
        self.params = {1: 41, 2: -5, 3: 3, 4: 1, 5: 30, 6: 250, 7: 380, 8: 485, 9: 935, 10: 1, 11: 11, 12: 1}
        self.cv2_ready.emit()

    @pyqtSlot(ndarray)
    def pass_frame(self, frame):
        self.frame = frame
        self.well = None
        print('Frame passed')
        self.cv2_ready.emit()

    @pyqtSlot(dict)
    def pass_params(self, params):
        self.params = params

    @pyqtSlot(bool)
    def find_well(self, show_result=True):
        print('Finding Circles')
        p = self.params
        frame = self.frame.copy()
        cimg = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        # blurred = cv2.medianBlur(cimg, 11)
        # blurred[blurred > 225] = 0
        # cimg = frame[:, :, 1]

        min_r = round(cimg.shape[0] * 0.001 * p[7])
        max_r = round(cimg.shape[0] * 0.001 * p[8])
        # print([min_r, max_r])
        circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, dp=p[3], minDist=p[4],
                                   param1=p[5], param2=p[6], minRadius=min_r, maxRadius=max_r)
        # circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, dp=3, minDist=1,
        #                            param1=30, param2=500, minRadius=min_r, maxRadius=max_r)
        if circles is not None:
            circles = uint16(around(circles))
            # print(circles)
            if len(circles) == 1:
                self.well = circles[0, 0]
                x = int(self.well[0])
                y = int(self.well[1])
                radius = int(self.well[2])
                if show_result is False:
                    print('Well found, not showing')
                    self.cv2_ready.emit()
                    return
                # smallest = self.well
                # c = x*x + y*y
                # for i in circles[0, :]:
                #     cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
                #     cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
                #     ci = int(i[0])*i[0] + int(i[1])*i[1]
                #     if c - ci < 5 and i[2] < smallest[2]:
                #         smallest = i
                #     if smallest is None:
                #         smallest = i
                #     elif i[2] < smallest[2]:
                #         smallest = i
                #     print(i)
                # cv2.circle(frame, (smallest[0], smallest[1]), smallest[2], (0, 255, 0), 2)
                # cv2.circle(frame, (smallest[0], smallest[1]), 2, (0, 0, 255), 3)
                cv2.circle(frame, (x, y), radius, (255, 255, 0), 2)
                cv2.circle(frame, (x, y), p[9], (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                print('Found %i circles' % len(circles[0, :]))
                print(self.well[2])
        else:
            print('No Circles Found')
            self.cv2_ready.emit()
            return
        print('Masking and making derivative frames')
        h, w, c = frame.shape
        mask = zeros((h, w), uint8)
        cv2.circle(mask, (x, y), p[9], 1, thickness=-1)
        # mean_value, std = cv2.meanStdDev(cimg, mask=mask)
        # print(mean_value)
        # mean_value = round(mean_value[0][0])
        # # max_value = mean_value - round(std[0][0])
        # max_value = mean_value + round(std[0][0] * 0.75)
        # max_value = mean_value
        # cimg[cimg > max_value] = max_value

        # r_sub_g = cv2.subtract(frame[:, :, 0], frame[:, :, 1])
        r_sub_g = frame[:, :, 1]

        if p[11] % 2 == 1:
            blurred = cv2.medianBlur(r_sub_g, p[11])
        else:
            blurred = cv2.medianBlur(cimg, p[11]+1)

        AT = cv2.adaptiveThreshold
        gauss = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        mean_c = cv2.ADAPTIVE_THRESH_MEAN_C
        reg = cv2.THRESH_BINARY
        inv = cv2.THRESH_BINARY_INV
        print('Processing threshold/edge')
        if p[10] < 13 and p[1] % 2 == 0:
            p[1] = p[1] + 1
        if p[10] == 1:
            thresh = cv2.adaptiveThreshold(cimg, 255, gauss, reg, p[1], p[2])
        elif p[10] == 2:
            thresh = cv2.adaptiveThreshold(cimg, 255, gauss, inv, p[1], p[2])
        elif p[10] == 3:
            thresh = cv2.adaptiveThreshold(cimg, 255, mean_c, reg, p[1], p[2])
        elif p[10] == 4:
            thresh = cv2.adaptiveThreshold(cimg, 255, mean_c, inv, p[1], p[2])
        elif p[10] == 5:
            thresh = cv2.adaptiveThreshold(r_sub_g, 255, gauss, reg, p[1], p[2])
        elif p[10] == 6:
            thresh = cv2.adaptiveThreshold(r_sub_g, 255, gauss, inv, p[1], p[2])
        elif p[10] == 7:
            thresh = cv2.adaptiveThreshold(r_sub_g, 255, mean_c, reg, p[1], p[2])
        elif p[10] == 8:
            thresh = cv2.adaptiveThreshold(r_sub_g, 255, mean_c, inv, p[1], p[2])
        elif p[10] == 9:
            thresh = cv2.adaptiveThreshold(blurred, 255, gauss, reg, p[1], p[2])
        elif p[10] == 10:
            thresh = cv2.adaptiveThreshold(blurred, 255, gauss, inv, p[1], p[2])
        elif p[10] == 11:
            thresh = cv2.adaptiveThreshold(blurred, 255, mean_c, reg, p[1], p[2])
        elif p[10] == 12:
            thresh = cv2.adaptiveThreshold(blurred, 255, mean_c, inv, p[1], p[2])
        elif p[10] == 13:
            canny = cv2.Canny(cimg, threshold1=p[1], threshold2=p[2], apertureSize=p[11], L2gradient=True)
        elif p[10] == 14:
            canny = cv2.Canny(r_sub_g, threshold1=p[1], threshold2=p[2], apertureSize=p[11], L2gradient=True)
        elif p[10] == 15:
            canny = cv2.Canny(blurred, threshold1=p[1], threshold2=p[2], apertureSize=5, L2gradient=True)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel, iterations=2)
        if p[10] <= 12:
            if p[12] == 1:
                if p[10] in [9, 10, 11, 12]:
                    k = 4
                else:
                    k = p[11]
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
                # kernel_s = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
                # thresh = cv2.dilate(thresh, kernel_s, iterations=2)
            overlay = thresh
        else:
            overlay = canny

        overlay = cv2.bitwise_and(overlay, overlay, mask=mask)
        print('Finding Contours')
        contours, hierarchy = cv2.findContours(overlay, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours is None or hierarchy is None:
            print('No contours found')
            return
        hierarchy = hierarchy[0]
        print(len(contours))
        # if p[10] in [1, 3, 5, 7, 9, 11]:
        #     r_contours = []
        #     target_parent = -1
        #     for item in zip(hierarchy, contours):
        #         h = item[0]
        #         # print(h)
        #         if h[3] > -1:
        #             if target_parent == -1:
        #                 target_parent = h[3]
        #                 r_contours.append(item[1])
        #             elif target_parent == h[3]:
        #                 r_contours.append(item[1])
        #     print(len(r_contours))
        #     contours = r_contours
        print('Sorting contours by area')
        areas = []
        for contour in contours:
            areas.append(cv2.contourArea(contour))
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:25]
        likely_hydra = []
        for c in contours:
            if 10000 > cv2.contourArea(c) > 500:
                likely_hydra.append(c)
        # frame = thresh
        # frame[cimg >= max_value] = [0, 0, 0]
        print('Drawing to frame')
        frame[overlay == 255] = [255, 0, 127]
        cv2.drawContours(frame, likely_hydra, -1, (0, 0, 255), 2)
        if len(frame.shape) == 3:
            h, w, c = frame.shape
        else:
            h, w = frame.shape
            c = 1
        if c == 1:
            img_format = QImage.Format_Grayscale8
        else:
            img_format = QImage.Format_RGB888
        pMap = QPixmap.fromImage(QImage(frame.copy().data, w, h, w * c, img_format))
        print('Showing well')
        self.show_cv2.emit(pMap)
        self.cv2_ready.emit()


class ZbarWorker(QObject):

    showCode = pyqtSignal(QPixmap)
    # showCode = pyqtSignal(ndarray)
    newScans = pyqtSignal(list)
    qrReady = pyqtSignal()

    def __init__(self, parent=None, crop = 1/2, factor = 1):
        super(self.__class__, self).__init__(parent)
        self.crop = crop
        self.factor = factor
        self.qrReady.emit()

    @pyqtSlot(ndarray)
    def decodeQR(self, frame):
        now = time()
        x_count = round(frame.shape[0] * self.crop)
        x_start = round((frame.shape[0] - x_count) / 2)
        x_stop = frame.shape[0] - x_start
        y_count = round(frame.shape[1] * self.crop)
        y_start = round((frame.shape[1] - y_count) / 2)
        y_stop = frame.shape[1] - y_start

        if self.factor > 1:
            yNew = round(x_count / self.factor)
            xNew = round(y_count / self.factor)
            barcodes = pyzbar.decode(cv2.resize(frame[x_start:x_stop, y_start:y_stop, :], (xNew, yNew)), symbols=[ZBarSymbol.QRCODE])
        else:
            barcodes = pyzbar.decode(frame[x_start:x_stop, y_start:y_stop, :], symbols=[ZBarSymbol.QRCODE])
        QThread.yieldCurrentThread()
        if len(barcodes) > 0:
            if len(frame.shape) == 3:
                h, w, c = frame.shape
            else:
                h, w = frame.shape
                c = 1
            if c == 1:
                img_format = QImage.Format_Grayscale8
            else:
                img_format = QImage.Format_RGB888
            qrlist = []
            for barcode in barcodes:
                bData = barcode.data.decode('utf-8')
                qrlist.append(bData)
                (x, y, wr, hr) = barcode.rect
                (x, y, wr, hr) = ((x * self.factor) + y_start, (y * self.factor) + x_start, wr * self.factor, hr * self.factor)
                if c > 1:
                    cv2.rectangle(frame, (x, y), (x + wr, y + hr), (0, 0, 255), 2)
                    cv2.putText(frame, bData, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (x, y), (x + wr, y + hr), 50, 2)
                    cv2.putText(frame, bData, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, 50, 2)
            pMap = QPixmap.fromImage(QImage(frame.copy().data, w, h, w * c, img_format))
            self.showCode.emit(pMap)
            self.newScans.emit(qrlist)
            print('QR Found: %s' % str(qrlist))
        else:
            print('No QR found')
        self.qrReady.emit()


# create class for our Raspberry Pi GUI
class MainWindow(QMainWindow, hydragui.Ui_MainWindow):
    # access variables inside of the UI's file

    camStartSignal = pyqtSignal(cv2.VideoCapture, name='camStartSignal')
    camStopSignal = pyqtSignal(name='camStopSignal')
    decodeQrSignal = pyqtSignal(ndarray, name='decodeQrSignal')
    cv2_pass_frame_signal = pyqtSignal(ndarray)
    cv2_pass_params_signal = pyqtSignal(dict)
    find_well_signal = pyqtSignal(bool)
    ot2_command_signal = pyqtSignal(str, name='ot2_command_signal')
    ot2_connect_signal = pyqtSignal(str, int, name='ot2_connect_signal')
    pt2_home_signal = pyqtSignal()
    pt2_home_z_signal = pyqtSignal()
    ot2_cam_to_signal = pyqtSignal(str, str, float, name='ot2_cam_to_signal')

    def toggleFullscreen(self):
        if self.windowState() & Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.databaseImageResize(0, 0)
        self.snapImageResize()

    def setImage(self, image):
        if image is None:
            return
        self.rgbImg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.new_image = True
        if self.doPreview is False:
            return
        shape = self.rgbImg.shape
        if self.cam_width is None or self.cam_width != shape[1]:
            self.cam_height, self.cam_width, channel = self.rgbImg.shape
            self.cam_bytes_per_line = channel * self.cam_width
            print((self.cam_width, self.cam_height))
        pMap = QPixmap.fromImage(
            QImage(self.rgbImg.data, self.cam_width, self.cam_height, self.cam_bytes_per_line, QImage.Format_RGB888)
        )
        preview_size = self.CamPreviewLabel.geometry()
        self.CamPreviewLabel.setPixmap(pMap.scaled(preview_size.width(), preview_size.height(), Qt.KeepAspectRatio))

    def capturedImage(self, ID, img):
        self.pixmap_image = QPixmap(img)
        img = img.convertToFormat(QImage.Format_RGB888)
        width = img.width()
        height = img.height()
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        self.rgbImg = array(ptr).reshape(height, width, 3)
        self.image_ready = True

    def procImage(self, pMap=None):
        if pMap is None:
            if self.rgbImg is None:
                return
            pMap = QPixmap.fromImage(
                QImage(self.rgbImg.data, self.cam_width, self.cam_height, self.cam_bytes_per_line, QImage.Format_RGB888)
            )
        self.snap_image = pMap
        s = self.SnapLabel.size()
        self.SnapLabel.setPixmap(pMap.scaled(s.width(), s.height(), Qt.KeepAspectRatio))

    def snapImageResize(self):
        if self.snap_image is None:
            return
        w = self.SnapLabel.geometry().width()
        h = self.SnapLabel.geometry().height()
        self.SnapLabel.setPixmap(self.snap_image.scaled(w, h, Qt.KeepAspectRatio))

    def checkBlur(self, image=None, threshold=100, crop=False):
        # Focus metric is the variance of the image convolved with the Laplacian kernel
        if not image:
            image = self.rgbImg
        if crop:
            x_count = round(image.shape[0] * self.qr_crop)
            x_start = round((image.shape[0] - x_count) / 2)
            x_stop = image.shape[0] - x_start
            y_count = round(image.shape[1] * self.qr_crop)
            y_start = round((image.shape[1] - y_count) / 2)
            y_stop = image.shape[1] - y_start
            focus = cv2.Laplacian(image[x_start:x_stop, y_start:y_stop, 1], cv2.CV_64F).var()
        else:
            focus = cv2.Laplacian(image[:, :, 0], cv2.CV_64F).var()
        if focus >= threshold:
            print('Not blurry: %s' % str(focus))
            return True
        else:
            print('Blurry: %s' % str(focus))
            return False

    def scanQR(self):
        for i in range(5):
            while self.new_image is False:
                QCoreApplication.processEvents()
            img = self.rgbImg.copy()
            self.new_image = False
            while self.qr_ready is False:
                QCoreApplication.processEvents()
            if self.checkBlur(threshold=100, crop=True):
                self.qr_ready = False
                self.decodeQrSignal.emit(img)

                return
        print('Blurry, no scan made')

    def scan_well(self):
        for i in range(5):
            while self.new_image is False:
                QCoreApplication.processEvents()
            img = self.rgbImg.copy()
            self.new_image = False
            while self.cv2_ready is False:
                QCoreApplication.processEvents()
            if self.checkBlur(threshold=10):
                self.cv2_ready = False
                self.cv2_pass_frame_signal.emit(img)
                while self.cv2_ready is False:
                    QCoreApplication.processEvents()
                self.cv2_ready = False
                d = {}
                d.update({1: self.snap_param_1.value()})
                d.update({2: self.snap_param_2.value()})
                d.update({3: self.snap_param_3.value()})
                d.update({4: self.snap_param_4.value()})
                d.update({5: self.snap_param_5.value()})
                d.update({6: self.snap_param_6.value()})
                d.update({7: self.snap_param_7.value()})
                d.update({8: self.snap_param_8.value()})
                d.update({9: self.snap_param_9.value()})
                d.update({10: self.snap_param_10.value()})
                d.update({11: self.snap_param_11.value()})
                d.update({12: self.snap_param_12.value()})
                self.cv2_pass_params_signal.emit(d)
                self.find_well_signal.emit(True)
                return
        print('Blurry, no scan made')

    def createQR(self, qrdata=None, savename=None):
        #  savename must contain the full path and extension to properly save the QR code, saves as PNG
        if qrdata is None or qrdata is False:
            qrdata = self.plateIDLineEdit.text()
            if len(qrdata) == 0:
                qrdata = 'Hydra~XXX-20201231001'
            savename = os.path.join(os.getcwd(), '%s.png' % qrdata)
            print(savename)
        else:
            print('qrdata passed')
            print(qrdata)
        qr = segno.make(qrdata, version=3, error='L')
        self.qrData = qrdata
        if savename is not None and savename is not False:
            try:
                qr.save(savename, border=4, scale=1, dpi=72)
                print('QR Code saved to: ' + savename)
                self.qrFile = savename
            except:
                print('QR Code save failed to path: ' + str(savename))
        self.plateList.update({qrdata: savename})
        self.QRDispLabel.setPixmap(QPixmap.fromImage(QImage(savename)).scaled(288, 288, Qt.KeepAspectRatio))
        item = QListWidgetItem(qrdata, self.plateListWidget)
        self.plateListWidget.setCurrentItem(item)

    def plate_list_changed(self, item):
        data = item.text()
        fn = self.plateList[data]
        self.qrData = data
        self.qrFile = fn
        try:
            self.QRDispLabel.setPixmap(QPixmap.fromImage(QImage(fn)).scaled(288, 288, Qt.KeepAspectRatio))
        except:
            print("Couldn't load QR Code File")

    def update_deck(self, manifest):
        self.plates_on_deck = manifest

    def updateScans(self, qrlist):
        self.scans += len(qrlist)
        self.scansLabel.setText(str(self.scans))
        self.codeList = qrlist
        qrdata = list(qrlist)[0]
        if qrdata not in self.plateList:
            savename = os.path.join(os.getcwd(), '%s.png' % qrdata)
            self.createQR(qrdata=qrdata, savename=savename)

    def emailQR(self):
        self.email_label_reset()
        self.sendEmailButton.setEnabled(False)
        self.sendEmailButton.repaint()
        address = self.emailLineEdit.text()
        password = self.passLineEdit.text()
        recipient = self.emailToLineEdit.text()
        if len(address) == 0 or len(password) == 0 or len(recipient) == 0:
            self.emailStatusLabel.setText('Need Email Info')
            self.email_status_timer.start(3000)
            self.sendEmailButton.setEnabled(True)
            return
        smtp_addr = self.SMTPLineEdit.text()
        if len(smtp_addr) == 0:
            smtp_addr = 'smtp.gmail.com'
        try:
            server = smtplib.SMTP(smtp_addr, 587)
            server.starttls()
            server.login(address, password)
        except Exception as e:
            print(e)
            print('Could not log into SMTP server, is your account set to allow SMTP connections?: ' + smtp_addr)
            self.emailStatusLabel.setText('SMTP login failed')
            self.emailStatusLabel.setStyleSheet('color: red; font-size: 14pt;')
            self.email_status_timer.start(3000)
            self.sendEmailButton.setEnabled(True)
            return
        msg = MIMEMultipart()
        msg['From'] = address
        msg['To'] = recipient
        items = self.plateListWidget.selectedItems()
        msg['Subject'] = 'HydraBot New Plate QR Codes'
        body = 'Here are the new plate QR codes that were generated.\n'
        for item in items:
            body += '%s\n' % item.text()
        msg.attach(MIMEText(body, 'plain'))
        items = self.plateListWidget.selectedItems()
        for item in items:
            data = item.text()
            fn = self.plateList[data]
            pic = open(fn, 'rb')
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(pic.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', 'attachment; filename=%s' % data + '.png')
            msg.attach(p)
        text = msg.as_string()
        server.sendmail(address, recipient, text)
        server.quit()
        self.plateListWidget.clearSelection()
        self.emailStatusLabel.setText('Email Sent')
        self.emailStatusLabel.setStyleSheet('color: green; font-size: 14pt;')
        self.email_status_timer.start(3000)
        self.sendEmailButton.setEnabled(True)

    def email_label_reset(self):
        self.emailStatusLabel.setText('')
        self.emailStatusLabel.setStyleSheet('color: black; font-size: 14pt;')

    def togglePreview(self):
        if self.previewCheckBox.isChecked():
            self.doPreview = True
        else:
            self.doPreview = False

    def qrReady(self):
        self.qr_ready = True

    def cv2_ready_slot(self):
        self.cv2_ready = True

    def cv2_reprocess(self):
        d = {}
        d.update({1: self.snap_param_1.value()})
        d.update({2: self.snap_param_2.value()})
        d.update({3: self.snap_param_3.value()})
        d.update({4: self.snap_param_4.value()})
        d.update({5: self.snap_param_5.value()})
        d.update({6: self.snap_param_6.value()})
        d.update({7: self.snap_param_7.value()})
        d.update({8: self.snap_param_8.value()})
        d.update({9: self.snap_param_9.value()})
        d.update({10: self.snap_param_10.value()})
        d.update({11: self.snap_param_11.value()})
        d.update({12: self.snap_param_12.value()})
        self.cv2_pass_params_signal.emit(d)
        self.find_well_signal.emit(True)

    def camStopped(self):
        self.cameraStopped = True

    def set_camera_exposure_mode(self, index):
        # mode = self.exposureModeComboBox.itemData(index)
        # self.cam_exposure.setExposureMode(mode)
        # if self.cam_exposure.exposureMode() == 1:
        #     shutter, _ = self.cam_exposure.supportedShutterSpeeds()
        #     print(shutter)
        #     print(self.cam_exposure.shutterSpeed())
        #     self.cam_exposure.setManualShutterSpeed(1.0)
        print(self.cam.imageProcessing().brightness())
        print(self.cam.imageProcessing().contrast())
        print(self.cam.imageProcessing().saturation())
        imgProc = self.cam.imageProcessing()
        if imgProc.isAvailable():
            imgProc.setWhiteBalanceMode(index)
            print(imgProc.WhiteBalanceMode())

    def set_camera_shutter_speed(self):
        val = self.camShutterBox.value()
        if val == 0:
            self.cam.exposure().setAutoShutterSpeed()
        self.cam.exposure().setManualShutterSpeed(val)
        print(self.cam.exposure().shutterSpeed())

    def camera_error(self, code):
        self.cam_error = code
        if code > 1:
            print('QCamera Error: %i')

    def get_input(self, title='HydraBot', question='Name:', default=''):
        question = question.ljust(len(title) + 15)
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(16)
        input_dialog = QInputDialog(self)
        input_dialog.setInputMode(QInputDialog.TextInput)
        input_dialog.setWindowTitle(title)
        input_dialog.setLabelText(question)
        input_dialog.setTextValue(default)
        input_dialog.setFont(font)
        input_dialog.setFixedWidth((50 + len(title)*5))
        ok = input_dialog.exec_()
        if ok:
            return input_dialog.textValue()
        else:
            return ''

    def list_select(self, options, title='HydraBot', question='Pick One:'):
        question = question.ljust(len(title) + 15)
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(16)
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle(title)
        input_dialog.setLabelText(question)
        input_dialog.setFont(font)
        input_dialog.setFixedWidth((50 + len(title) * 5))
        input_dialog.setComboBoxItems(options)
        ok = input_dialog.exec_()
        if ok:
            return input_dialog.textValue()
        else:
            return ''

    def tree_menu(self, position):
        item = self.databaseTreeWidget.selectedItems()[0]
        self.activateTreeItem(item)
        level = item.data(0, Qt.UserRole)
        menu = QMenu(self.databaseTreeWidget)
        if level != 'event':
            if level == 'colony':
                nameAction = menu.addAction('Edit ID')
                locationAction = menu.addAction('Edit Location')
            else:
                nameAction = menu.addAction('Edit Name')
                locationAction = None
            populationBeforeAction = None
            populationAfterAction = None
            locationBeforeAction = None
            locationAfterAction = None
        else:
            nameAction = menu.addAction('Edit Event Type')
            population_menu = menu.addMenu('Edit Population...')
            populationBeforeAction = population_menu.addAction('Before')
            populationAfterAction = population_menu.addAction('After')
            location_menu = menu.addMenu('Edit Location...')
            locationBeforeAction = location_menu.addAction('Before')
            locationAfterAction = location_menu.addAction('After')
            locationAction = None
        timeAction = menu.addAction('Edit Time')
        img_menu = menu.addMenu('Images...')
        if level == 'event':
            imageBeforeAction = img_menu.addAction('Before Event')
            imageAfterAction = img_menu.addAction('After Event')
            stereotypeAction = None
        else:
            stereotypeAction = img_menu.addAction('Stereotype')
            imageBeforeAction = None
            imageAfterAction = None
        iconAction = img_menu.addAction('Tree Icon')
        action = menu.exec_(self.databaseTreeWidget.mapToGlobal(position))
        if action is None:
            return
        elif action == nameAction:
            self.edit_name(item)
        elif action == timeAction:
            self.edit_time(item)
        elif action == locationAction:
            self.edit_location(item)
        elif action == populationBeforeAction:
            self.edit_population(item, 'before')
        elif action == populationAfterAction:
            self.edit_population(item, 'after')
        elif action == locationBeforeAction:
            self.edit_location(item, 'before')
        elif action == locationAfterAction:
            self.edit_location(item, 'after')
        elif action == imageBeforeAction:
            self.edit_image(item, 'before')
        elif action == imageAfterAction:
            self.edit_image(item, 'after')
        elif action == stereotypeAction:
            self.edit_image(item, 'stereotype')
        elif action == iconAction:
            self.edit_image(item, 'icon')

    def database_image_menu(self, position):
        approach = self.event_image_display_approach
        # event image display, choose from: 'before', 'after', 'stacked', 'side-by-side', 'overlay'
        menu = QMenu(self.databaseTreeWidget)
        # img_menu = menu.addMenu('Event Images Display')
        before_action = menu.addAction('Before')
        if approach == 'before':
            before_action.setChecked(True)
        after_action = menu.addAction('After')
        if approach == 'after':
            after_action.setChecked(True)
        stacked_action = menu.addAction('Stacked')
        if approach == 'stacked':
            stacked_action.setChecked(True)
        side_action = menu.addAction('Side by Side')
        if approach == 'side-by-side':
            side_action.setChecked(True)
        overlay_action = menu.addAction('Overlay')
        if approach == 'overlay':
            overlay_action.setChecked(True)
        save_action = menu.addAction('Save...')
        action = menu.exec_(self.databaseImageLabel.mapToGlobal(position))
        if action is None:
            return
        elif action == before_action:
            self.event_image_display_approach = 'before'
        elif action == after_action:
            self.event_image_display_approach = 'after'
        elif action == stacked_action:
            self.event_image_display_approach = 'stacked'
        elif action == side_action:
            self.event_image_display_approach = 'side-by-side'
        elif action == overlay_action:
            self.event_image_display_approach = 'overlay'
        elif action == save_action:
            filename = QFileDialog.getSaveFileName(self, 'Save Image To...')
            filename, encoding = check_image_format(filename[0])
            self.databasePixmap.save(filename, encoding)
        item = self.last_selected_tree_item
        if item and item.data(0, Qt.UserRole) == 'event' and approach != self.event_image_display_approach:
            img = self.create_event_image(item.data(1, Qt.UserRole))
            self.databasePixmap = img
            self.databaseImageResize(0, 0)

    def snap_label_menu(self, position):
        menu = QMenu(self.databaseTreeWidget)
        save_action = menu.addAction('Save...')
        action = menu.exec_(self.databaseImageLabel.mapToGlobal(position))
        if action is None:
            return
        elif action == save_action:
            filename = QFileDialog.getSaveFileName(self, 'Save Image To...')
            filename, encoding = check_image_format(filename[0])
            self.snap_image.save(filename, encoding)

    def view_menu(self, position):
        menu = QMenu(self.databaseTreeWidget)
        save_action = menu.addAction('Save...')
        action = menu.exec_(self.databaseImageLabel.mapToGlobal(position))
        if action is None:
            return
        elif action == save_action:
            self.image_ready = False
            self.cam_shutter.capture()
            while self.image_ready is False:
                QCoreApplication.processEvents()
            filename = QFileDialog.getSaveFileName(self, 'Save Image To...')
            filename, encoding = check_image_format(filename[0])
            self.pixmap_image.save(filename, encoding)

    def edit_name(self, item):
        level = item.data(0, Qt.UserRole)
        db_item = item.data(1, Qt.UserRole)
        if level == 'stock':
            name = self.get_input(title='HydraBot - Edit Stock', question='Stock Name:', default=db_item.name)
            if name == '':
                return None
            for stock in self.Stocks:
                if name == stock:
                    _ = QMessageBox.question(self, 'HydraBot - Edit Stock', 'Name already in use: %s' % name,
                                             QMessageBox.Ok, QMessageBox.Ok)
                    return None
            db_item.name = name
            item.setText(0, name)
        if level == 'animal':
            name = self.get_input(title='HydraBot - Edit Animal', question='Animal Name:', default=db_item.name)
            if name == '':
                return None
            for animal in db_item.parent:
                if name == animal.name:
                    _ = QMessageBox.question(self, 'HydraBot - Edit Animal', 'Name already in use: %s' % name,
                                             QMessageBox.Ok, QMessageBox.Ok)
                    return None
            db_item.name = name
            item.setText(0, name)
        if level == 'colony':
            name = self.get_input(title='HydraBot - Edit Colony', question='Colony ID:', default=db_item.name)
            if name == '':
                return None
            try:
                ID = int(name)
            except:
                _ = QMessageBox.question(self, 'HydraBot - Edit Colony', 'ID must be an integer',
                                         QMessageBox.Ok, QMessageBox.Ok)
                return None
            for colony in db_item.parent:
                if name == colony.name:
                    _ = QMessageBox.question(self, 'HydraBot - Edit Colony', 'ID already in use: %s' % name,
                                             QMessageBox.Ok, QMessageBox.Ok)
                    return None
            db_item.name = name
            db_item.ID = ID
            item.setText(0, name)
        if level == 'event':
            name = self.get_input(title='HydraBot - Edit Event', question='Edit Event Type:', default=db_item.event)
            if name == '':
                return None
            db_item.event = name
            db_item.name = name + '~' + hydradb.get_date_string(db_item)
            item.setText(0, name)

    def edit_time(self, item):
        _ = QMessageBox.question(self, 'HydraBot - Edit Time', "You really shouldn't and right now, you can't",
                                 QMessageBox.Ok, QMessageBox.Ok)

    def edit_location(self, item, before_after=None):
        level = item.data(0, Qt.UserRole)
        db_item = item.data(1, Qt.UserRole)
        if level == 'colony':
            if len(self.plateList) == 0:
                print('No plates available for new location')
                return None
            plate = self.list_select(self.plateList, 'HydraBot - Colony Location', 'Select a Plate:')
            if plate == '':
                return None
            well_list = ('A1', 'A2', 'A3', 'B1', 'B2', 'B3')
            well = self.list_select(well_list, 'HydraBot - Colony Location', 'Which well in plate %s:' % plate)
            if well == '':
                return None
            db_item.plate = plate
            db_item.well = well
            db_item.location = '%s:%s' % (plate, well)
            item.setText(2, db_item.location)
        elif level == 'event':
            if before_after == 'before':
                if len(self.plateList) == 0:
                    print('No plates available for new location')
                    return None
                plate = self.list_select(self.plateList, 'HydraBot - Location Before', 'Select a Plate:')
                if plate == '':
                    return None
                well_list = ('A1', 'A2', 'A3', 'B1', 'B2', 'B3')
                well = self.list_select(well_list, 'HydraBot - Location Before', 'Which well in plate %s:' % plate)
                if well == '':
                    return None
                location = '%s:%s' % (plate, well)
                db_item.location_before = location
                if location == db_item.location_after:
                    location_str = location
                elif db_item.location_after:
                    location_str = location + ' / ' + db_item.location_after
                else:
                    location_str = location
                item.setText(2, location_str)
            elif before_after == 'after':
                if len(self.plateList) == 0:
                    print('No plates available for new location')
                    return None
                plate = self.list_select(self.plateList, 'HydraBot - Location After', 'Select a Plate:')
                if plate == '':
                    return None
                well_list = ('A1', 'A2', 'A3', 'B1', 'B2', 'B3')
                well = self.list_select(well_list, 'HydraBot - Location After', 'Which well in plate %s:' % plate)
                if well == '':
                    return None
                location = '%s:%s' % (plate, well)
                if db_item == db_item.parent.latest_event:
                    db_item.parent.plate = plate
                    db_item.parent.well = well
                    db_item.parent.location = location
                    item.parent().setText(2, location)
                db_item.location_after = location
                if location == db_item.location_before:
                    location_str = location
                else:
                    location_str = db_item.location_before + ' / ' + location
                item.setText(2, location_str)
        self.get_plate_manifest()

    def edit_population(self, item, before_after=None):
        db_item = item.data(1, Qt.UserRole)
        if before_after == 'before':
            population = self.get_input(title='HydraBot - Edit Event', question='Population Before Event:')
            if population == '':
                return None
            try:
                count = int(population)
            except:
                _ = QMessageBox.question(self, 'HydraBot - Edit Event', "Population must be an integer",
                                         QMessageBox.Ok, QMessageBox.Ok)
                return None
            db_item.population_before = count
            item.setText(3, population + ' / ' + str(db_item.population_after))
        elif before_after == 'after':
            population = self.get_input(title='HydraBot - Edit Event', question='Population After Event:')
            if population == '':
                return None
            try:
                count = int(population)
            except:
                _ = QMessageBox.question(self, 'HydraBot - Edit Event', "Population must be an integer",
                                         QMessageBox.Ok, QMessageBox.Ok)
                return None
            db_item.population_after = count
            item.setText(3, '%i / %s' % (db_item.population_before, population))
            if db_item == db_item.parent.latest_event:
                db_item.stock.update_population()
                colony_w = item.parent()
                colony_w.setText(3, population)
                animal_w = colony_w.parent()
                animal = animal_w.data(1, Qt.UserRole)
                animal_w.setText(3, str(animal.population))
                stock_w = animal_w.parent()
                stock = stock_w.data(1, Qt.UserRole)
                stock_w.setText(3, str(stock.population))

    def edit_image(self, item, image_type):
        db_item = item.data(1, Qt.UserRole)
        if image_type == 'icon':
            msg_text = '<html>Images larger than 48x48 will be resized <br><br> Get Image From...'
        else:
            msg_text = 'Get Image From...'
        msg_box = QMessageBox(self)
        font = msg_box.font()
        font.setPointSize(14)
        msg_box.setFont(font)
        msg_box.setWindowTitle('HydraBot Image')
        msg_box.setText(msg_text)
        file_button = msg_box.addButton('File', QMessageBox.YesRole)
        camera_button = msg_box.addButton('Camera', QMessageBox.NoRole)
        cancel_button = msg_box.addButton('Cancel', QMessageBox.RejectRole)
        response = msg_box.exec_()
        if msg_box.clickedButton() == file_button:
            print('Selecting image from file')
            fname = QFileDialog.getOpenFileName(self, 'Choose Image')
            pMap = QPixmap.fromImage(QImage(fname[0]))
        elif msg_box.clickedButton() == camera_button:
            pMap = None
            self.MainTabs.setCurrentIndex(0)
            response = QMessageBox.question(self, 'HydraBot Capture', 'Capture Image?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            # noinspection PyArgumentList
            if response == QMessageBox.Yes:
                self.image_ready = False
                self.cam_shutter.capture()
                while self.image_ready is False:
                    QCoreApplication.processEvents()
                # noinspection PyCallByClass
                pMap = self.pixmap_image
                print('Image Captured')
            else:
                print('Set image canceled')
                self.MainTabs.setCurrentIndex(3)
                return
            self.MainTabs.setCurrentIndex(3)
        else:
            return
        if image_type == 'icon':
            print(image_type)
            pMap = pMap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item.setIcon(0, QIcon(pMap))
            db_item.icon_image = pMap
        elif image_type == 'before':
            print(image_type)
            db_item.image_before = pMap
            img = self.create_event_image(item.data(1, Qt.UserRole))
            self.databasePixmap = img
            self.databaseImageResize(0, 0)
        elif image_type == 'after':
            print(image_type)
            db_item.image_after = pMap
            img = self.create_event_image(item.data(1, Qt.UserRole))
            self.databasePixmap = img
            self.databaseImageResize(0, 0)
        elif image_type == 'stereotype':
            print(image_type)
            db_item.stereotype_image = pMap
            self.databasePixmap = pMap
            self.databaseImageResize(0, 0)

    def activateTreeItem(self, item):
        self._activate_tree_item(item)

    def _activate_tree_item(self, item, recursive_call=False):
        level = item.data(0, Qt.UserRole)
        db_item = item.data(1, Qt.UserRole)
        if recursive_call is False:
            if item == self.last_selected_tree_item:
                return
            self.last_selected_tree_item = item
            self.addAnimalToolButton.setEnabled(False)
            self.addColonyToolButton.setEnabled(False)
            self.addEventToolButton.setEnabled(False)
        if level == 'stock':
            self.activeStock = item
            self.addAnimalToolButton.setEnabled(True)
        else:
            self._activate_tree_item(item.parent(), recursive_call=True)
            if level == 'animal':
                self.activeAnimal = item
                self.addColonyToolButton.setEnabled(True)
            elif level == 'colony':
                self.activeColony = item
                self.addEventToolButton.setEnabled(True)
            elif level == 'event':
                self.activeEvent = item
        if recursive_call is False:
            if level == 'event':
                img = self.create_event_image(db_item)
            else:
                if db_item.stereotype_image:
                    img = db_item.stereotype_image
                else:
                    img = QPixmap(':/HydraBot/Media/Hydra Fluor crop.jpg')
            try:
                self.databasePixmap = img
                self.databaseImageResize(0, 0)
            except:
                print('%s Image could not be displayed' % db_item.name)

    def create_event_image(self, db_item):
        if db_item.image_after and db_item.image_before:
            approach = self.event_image_display_approach
            if approach == 'before':
                img = db_item.image_before
            elif approach == 'after':
                img = db_item.image_after
            else:
                wb = db_item.image_before.width()
                wa = db_item.image_after.width()
                hb = db_item.image_before.height()
                ha = db_item.image_after.height()
                if approach == 'stacked':
                    w = max(wb, wa)
                    h = hb + ha
                    img = QPixmap(w, h)
                    painter = QPainter(img)
                    painter.drawPixmap(0, 0, wb, hb, db_item.image_before)
                    painter.drawPixmap(0, hb, wa, ha, db_item.image_after)
                    painter.end()
                elif approach == 'side-by-side':
                    h = max(hb, ha)
                    w = wb + wa
                    img = QPixmap(w, h)
                    painter = QPainter(img)
                    painter.drawPixmap(0, 0, wb, hb, db_item.image_before)
                    painter.drawPixmap(wb, 0, wa, ha, db_item.image_after)
                    painter.end()
                elif approach == 'overlay':
                    w = max(wb, wa)
                    h = max(hb, ha)
                    img = QPixmap(w, h)
                    painter = QPainter(img)
                    painter.drawPixmap(0, 0, wb, hb, db_item.image_before)
                    painter.setOpacity(0.5)
                    painter.drawPixmap(0, 0, wa, ha, db_item.image_after)
                    painter.end()
        elif db_item.image_after:
            img = db_item.image_after
        elif db_item.image_before:
            img = db_item.image_before
        else:
            img = QPixmap(':/HydraBot/Media/Hydra Fluor crop.jpg')
        return img

    def newStock(self):
        name = self.get_input(title='HydraBot - New Stock', question='Stock Name:')
        if name == '':
            return None
        return self._newStock(name)

    def _newStock(self, name, **kwargs):
        for stock in self.Stocks:
            if name == stock:
                return None
        stock = hydradb.Stock(name=name, **kwargs)
        if stock.icon_image is None:
            stock.icon_image = QPixmap(':/HydraBot/Media/stock_48.png')
        if stock.stereotype_image is None:
            stock.stereotype_image = QPixmap(':/HydraBot/Media/Hydra Fluor crop.jpg')
        stock_w = QTreeWidgetItem(self.databaseTreeWidget, [name, hydradb.get_date_string(stock), '', '0'])
        stock_w.setData(0, Qt.UserRole, 'stock')
        stock_w.setData(1, Qt.UserRole, stock)
        stock_w.setIcon(0, QIcon(stock.icon_image))
        self.Stocks.update({name: [stock, stock_w]})
        for item in self.databaseTreeWidget.selectedItems():
            item.setSelected(False)
        stock_w.setSelected(True)
        self.activateTreeItem(stock_w)
        return stock_w

    def newAnimal(self):
        name = self.get_input(title='HydraBot - New Animal', question='Animal Name:')
        if name == '':
            return None
        return self._newAnimal(name)

    def _newAnimal(self, name, **kwargs):
        stock_w = self.activeStock
        stock = stock_w.data(1, Qt.UserRole)
        if name in stock.names():
            return None
        animal = stock.add_animal(name, **kwargs)
        if animal.icon_image is None:
            animal.icon_image = QPixmap(':/HydraBot/Media/watermelon_48.png')
        if animal.stereotype_image is None:
            animal.stereotype_image = QPixmap(':/HydraBot/Media/Hydra Fluor crop.jpg')
        animal_w = QTreeWidgetItem(stock_w, [name, hydradb.get_date_string(animal), '', str(animal.population)])
        animal_w.setData(0, Qt.UserRole, 'animal')
        animal_w.setData(1, Qt.UserRole, animal)
        animal_w.setIcon(0, QIcon(animal.icon_image))
        stock_w.setExpanded(True)
        for item in self.databaseTreeWidget.selectedItems():
            item.setSelected(False)
        animal_w.setSelected(True)
        self.activateTreeItem(animal_w)
        return animal_w

    def newColony(self):
        # location = self.get_input(title='HydraBot - New Colony', question='Colony Location (PlateID:Well):')
        if len(self.plateList) == 0:
            print('No plates available for new colony')
            return None
        plate = self.list_select(self.plateList, 'HydraBot - New Colony', 'Select a Plate:')
        if plate == '':
            return None
        well_list = ('A1', 'A2', 'A3', 'B1', 'B2', 'B3')
        well = self.list_select(well_list, 'HydraBot - New Colony', 'Which well in plate %s:' % plate)
        if well == '':
            return None
        return self._newColony(plate, well, founding_event=True)

    def _newColony(self, plate, well, founding_event=False, **kwargs):
        self.get_plate_manifest()
        if plate in self.plate_manifest:
            if well in self.plate_manifest[plate]:
                print('Location already in use')
                return
        animal_w = self.activeAnimal
        animal = animal_w.data(1, Qt.UserRole)
        # kwargs = {'plate': plate, 'well': well}
        colony = animal.add_colony(plate=plate, well=well, **kwargs)
        name = colony.name
        pop = str(colony.population)
        if colony.icon_image is None:
            colony.icon_image = QPixmap(':/HydraBot/Media/fishbowl_48.png')
        if colony.stereotype_image is None:
            animal.stereotype_image = QPixmap(':/HydraBot/Media/Hydra Fluor crop.jpg')
        colony_w = QTreeWidgetItem(animal_w, [name, hydradb.get_date_string(colony), colony.location, pop])
        colony_w.setData(0, Qt.UserRole, 'colony')
        colony_w.setData(1, Qt.UserRole, colony)
        colony_w.setIcon(0, QIcon(colony.icon_image))
        animal_w.setExpanded(True)
        if founding_event:
            print('Creating Founded Event')
            event = colony.add_event('Founded')
            name = 'Founded'
            event.icon_image = QPixmap(':/HydraBot/Media/event_48.png')
            event_w = QTreeWidgetItem(colony_w, [name, hydradb.get_date_string(colony), colony.location, '0 / 0'])
            event_w.setData(0, Qt.UserRole, 'event')
            event_w.setData(1, Qt.UserRole, event)
            event_w.setIcon(0, QIcon(event.icon_image))
            colony_w.setExpanded(True)
            for item in self.databaseTreeWidget.selectedItems():
                item.setSelected(False)
            event_w.setSelected(True)
            self.activateTreeItem(event_w)
            return colony_w, event_w
        for item in self.databaseTreeWidget.selectedItems():
            item.setSelected(False)
        colony_w.setSelected(True)
        self.activateTreeItem(colony_w)
        self.get_plate_manifest()
        return colony_w

    def newEvent(self):
        name = self.get_input(title='HydraBot - New Event', question='Event Type:')
        if name == '':
            return None
        return self._newEvent(name)

    def _newEvent(self, name, **kwargs):
        colony_w = self.activeColony
        colony = colony_w.data(1, Qt.UserRole)
        if colony.latest_event is None:
            pop_before = 0
            pop_str = '0 / 0'
        else:
            pop_before = colony.latest_event.population_after
            pop_str = '%i / %i' % (pop_before, pop_before)
        event = colony.add_event(name, location_before=colony.location, location_after=colony.location,
                                 population_before=pop_before, population_after=pop_before, **kwargs)
        name = event.event
        if event.icon_image is None:
            event.icon_image = QPixmap(':/HydraBot/Media/event_48.png')
        event_w = QTreeWidgetItem(colony_w, [name, hydradb.get_date_string(event), event.location_before, pop_str])
        event_w.setData(0, Qt.UserRole, 'event')
        event_w.setData(1, Qt.UserRole, event)
        event_w.setIcon(0, QIcon(event.icon_image))
        colony_w.setExpanded(True)
        for item in self.databaseTreeWidget.selectedItems():
            item.setSelected(False)
        event_w.setSelected(True)
        self.activateTreeItem(event_w)
        return event_w

    def get_plate_manifest(self):
        if self.activeStock is None:
            return
        for i in range(self.plateManifestTreeWidget.topLevelItemCount()):
            _ = self.plateManifestTreeWidget.takeTopLevelItem(0)
        self.plate_manifest = hydradb.plate_manifest(self.activeStock.data(1, Qt.UserRole))
        for plate, wells in self.plate_manifest.items():
            # print(plate)
            plate_w = QTreeWidgetItem(self.plateManifestTreeWidget, [str(plate), '', ''])
            for well, info in wells.items():
                well_w = QTreeWidgetItem(plate_w, ['', well, '%s ~ %i' % (info[0], info[1])])
                well_w.setData(0, Qt.UserRole, info[2])
                plate_w.setExpanded(True)
                # print('   %s: %s ~ %i' % (well, info[0], info[1]))

    def ot2_connect(self):
        host = self.hostnameLineEdit.text()
        self.ot2_connect_signal.emit(host, 0)

    def ot2_connection_status(self, info):
        if info is None or len(info) == 0:
            self.ot2ServerConnectPushButton.setEnabled(True)
            self.ot2ServerDisconnectPushButton.setEnabled(False)
        else:
            self.ot2ServerConnectPushButton.setEnabled(False)
            self.ot2ServerDisconnectPushButton.setEnabled(True)

    def ot2_lights_on(self):
        self.ot2_command_signal.emit('robot.turn_on_rail_lights()')

    def ot2_lights_off(self):
        self.ot2_command_signal.emit('robot.turn_off_rail_lights()')

    def ot2_cmd(self):
        cmd = self.ot2CommandLineEdit.text()
        self.ot2_command_signal.emit(cmd)

    def ot2_error(self, err):
        print(err)

    def ot2_camera_to(self):
        plate = self.ot2SlotComboBox.currentIndex() + 1
        well = self.ot2WellComboBox.currentText()
        height = self.ot2HeightDoubleSpinBox.value()
        self.ot2_cam_to_signal.emit('plate_%i' % plate, well, height)

    def ot2_update_slot(self, slot, plate=None, activate=False):
        slots = {1: (3, 0), 2: (3, 1), 3: (3, 2),
                 4: (2, 0), 5: (2, 1), 6: (2, 2),
                 7: (1, 0), 8: (1, 1), 9: (1, 2),
                 10: (0, 0), 11: (0, 1), 12: (0, 2)}
        if slot in ('TRASH', 'trash', 'Trash'):
            slot = 12
        location = slots[slot]
        item = self.platesOnDeckTableWidget.item(location[0], location[1])
        if plate:
            if slot == 12:
                slot = 'TRASH'
            item.setText('%i\n%s' % (slot, plate))
        if activate:
            if self.ot2_current_slot_item:
                self.ot2_current_slot_item.setBackground(QBrush(Qt.NoBrush))
            self.ot2_current_slot_item = item
            h = self.platesOnDeckTableWidget.rowHeight(location[0])
            w = self.platesOnDeckTableWidget.columnWidth(location[1])
            cx = round(w / 2)
            cy = round(h / 2)
            gradient = QRadialGradient(cx, cy, min(cx, cy))
            gradient.setColorAt(0, QColor('white'))
            gradient.setColorAt(0.5, QColor('white'))
            gradient.setColorAt(1, QColor('darkCyan'))
            brush = QBrush(gradient)
            item.setBackground(brush)
            # self.platesOnDeckTableWidget.setCurrentCell(location[0], location[1])

        self.platesOnDeckTableWidget.repaint()

    def databaseImageResize(self, pos, ind):
        w = self.databaseImageLabel.geometry().width()
        h = self.databaseImageLabel.geometry().height()
        self.databaseImageLabel.setPixmap(self.databasePixmap.scaled(w, h, Qt.KeepAspectRatio))

    def tab_listener(self, index):
        if index == 1 and index == self.current_tab:
            page = (self.OT2StackedWidget.currentIndex() + 1) % self.OT2StackedWidget.count()
            self.OT2StackedWidget.setCurrentIndex(page)
        self.current_tab = index

    def debug_command(self):
        code = self.debugCommandLineEdit.text()
        self.debugCommandLineEdit.setText('')
        self.debugCommandsPlainTextEdit.appendPlainText('')
        self.debugCommandsPlainTextEdit.appendPlainText(code)
        self.debugCommandLineEdit.repaint()
        self.debug_locals.update(locals())
        with stdout_redirect() as out:
            try:
                retval = eval(code, globals(), self.debug_locals)
                if retval:
                    print(retval)
            except SyntaxError:
                try:
                    exec(code, globals(), self.debug_locals)
                except Exception as E:
                    print(E)
            except Exception as e:
                print(e)
        if len(out.getvalue()) > 0:
            self.debugOutputPlainTextEdit.appendPlainText(out.getvalue())

    def debug_clear(self):
        self.debugCommandsPlainTextEdit.clear()
        self.debugOutputPlainTextEdit.clear()

    def re_init_camera(self):
        if self.cam is not None:
            try:
                self.cam.stop()
                print('Camera stopped')
            except Exception as e:
                print(e)
            try:
                self.cam.unload()
                print('Camera Unloaded')
            except Exception as e:
                print(e)
            cam_list = QCameraInfo.availableCameras()
            num_cams = len(cam_list)
            if num_cams <= 0:
                return
            elif num_cams == 1:
                self.cam = QCamera(cam_list[0])
            else:
                cam_desc = []
                for camera in cam_list:
                    desc = camera.description()
                    suffix = ''
                    count = 1
                    while desc + suffix in cam_desc:
                        suffix = str(count)
                        count += 1
                    if count > 1:
                        desc = '%s_%s' % (desc, suffix)
                    cam_desc.append(desc)
                camera = self.list_select(cam_desc, 'HydraBot - Select Camera', 'Select a Camera:')
                if camera == '':
                    return None
                for i in range(num_cams):
                    if camera in cam_desc[i]:
                        self.cam = QCamera(cam_list[i])
                        break
        self.cam_shutter = QCameraImageCapture(self.cam)
        self.cam_shutter.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)
        self.cam_shutter.imageCaptured.connect(self.capturedImage)
        self.cam.setCaptureMode(QCamera.CaptureStillImage)
        self.cam_exposure = self.cam.exposure()
        self.cam_modes = []
        for mode in EXPOSURE_MODES:
            if self.cam_exposure.isExposureModeSupported(mode):
                self.cam_modes.append(mode)
                self.exposureModeComboBox.addItem(EXPOSURE_MODES[mode], mode)
        current_mode = self.cam_exposure.exposureMode()
        self.exposureModeComboBox.setCurrentIndex(self.exposureModeComboBox.findData(current_mode, Qt.UserRole))
        self.cam.setViewfinder(self.cam_view)
        self.cam_error = 0
        self.cam.error.connect(self.camera_error)
        self.cam.start()
        settings = self.cam.viewfinderSettings()
        resolutions = self.cam.supportedViewfinderResolutions()
        res_list = []
        for resolution in resolutions:
            res_list.append('%i x %i' % (resolution.width(), resolution.height()))
        resolution = self.list_select(res_list, 'HydraBot - Select Resolution', 'Select a Resolution:')
        if resolution == '':
            self.cam.stop()
            return None
        for i in range(len(res_list)):
            if resolution in res_list[i]:
                settings.setResolution(resolutions[i])
                break
        self.cam.setViewfinderSettings(settings)
        print('Camera Resolution set to %s' % res_list[i])
        self.image_ready = False
        print('cam initialized')

    def define_variables(self):
        self.current_tab = 0
        self.debug_locals = {}
        self.snap_image = None

    def createWidgets(self):
        self.fullscreenToolButton = QToolButton()
        self.fullscreenToolButton.setObjectName('fullscreenToolButton')
        self.fullscreenToolButton.setToolTip("Toggle Full Screen")
        self.fullscreenToolButton.setText("...")
        self.fullscreenToolButton.setIcon(QIcon(QPixmap(':/HydraBot/Media/full_screen.png')))
        self.fullscreenToolButton.setIconSize(QSize(48, 48))
        self.statusbar.addPermanentWidget(self.fullscreenToolButton)

        self.exitToolButton = QToolButton()
        self.exitToolButton.setObjectName('exitToolButton')
        self.exitToolButton.setToolTip("Exit HydraBot")
        self.exitToolButton.setText("...")
        self.exitToolButton.setIcon(QIcon(QPixmap(':/HydraBot/Media/dialog_close.png')))
        self.exitToolButton.setIconSize(QSize(48, 48))
        self.statusbar.addPermanentWidget(self.exitToolButton)

        self.email_status_timer = QTimer()

    def connectSignals(self):
        self.sendEmailButton.clicked.connect(self.emailQR)
        self.previewCheckBox.clicked.connect(self.togglePreview)
        self.plateIDLineEdit.returnPressed.connect(self.createQR)
        self.createPlateButton.clicked.connect(self.createQR)
        self.initCameraButton.clicked.connect(self.re_init_camera)
        self.scanQRButton.clicked.connect(self.scanQR)
        self.scanWellsButton.clicked.connect(self.scan_well)
        # self.ExitButton.clicked.connect(self.cleanClose)
        self.exitToolButton.clicked.connect(self.cleanClose)
        self.fullscreenToolButton.clicked.connect(self.toggleFullscreen)
        self.databaseSplitter.splitterMoved.connect(self.databaseImageResize)
        self.databaseTreeWidget.itemClicked.connect(self.activateTreeItem)
        self.SnapLabel.customContextMenuRequested.connect(self.snap_label_menu)
        self.CamPreviewLabel.customContextMenuRequested.connect(self.view_menu)
        self.databaseTreeWidget.customContextMenuRequested.connect(self.tree_menu)
        self.addStockToolButton.clicked.connect(self.newStock)
        self.addAnimalToolButton.clicked.connect(self.newAnimal)
        self.addColonyToolButton.clicked.connect(self.newColony)
        self.addEventToolButton.clicked.connect(self.newEvent)
        self.dataToolButton.clicked.connect(self.get_plate_manifest)
        self.databaseImageLabel.customContextMenuRequested.connect(self.database_image_menu)
        self.plateListWidget.currentItemChanged.connect(self.plate_list_changed)
        self.email_status_timer.timeout.connect(self.email_label_reset)
        self.MainTabs.tabBarClicked.connect(self.tab_listener)
        self.debugCommandLineEdit.returnPressed.connect(self.debug_command)
        self.debugClearPushButton.clicked.connect(self.debug_clear)

    def initCamera(self):
        self.cam = None
        self.cam_width = None
        self.cam_height = None
        self.cam_bytes_per_line = None
        self.rgbImg = None
        # self.CamPreviewLabel.setFixedHeight(480)
        # self.CamPreviewLabel.setFixedWidth(640)
        self.doPreview = True
        camera_count = 0
        # print('Finding Cameras')
        # for i in range(0, -1, -1):
        #     try:
        #         cam = cv2.VideoCapture(i)
        #         cam.getBackendName()
        #     except Exception:
        #         # print('ID number %i failed' % i)
        #         pass
        #     else:
        #         camera_count = i + 1
        #         cam.release()
        #         break
        # if camera_count == 0:
        #     print('No Cameras Found')
        #     self.cam = None
        #     return
        # elif camera_count == 1:
        #     self.cam = cv2.VideoCapture(0)
        # else:
        #     cam_desc = []
        #     for i in range(camera_count):
        #         cam_desc.append(str(i))
        #     camera = self.list_select(cam_desc, 'HydraBot - Select Camera', 'Select a Camera:')
        #     if camera == '':
        #         return None
        #     self.cam = cv2.VideoCapture(int(camera))
        self.cam = cv2.VideoCapture(0)
        self.cameraStopped = False
        backend = self.cam.getBackendName()
        print(backend)
        if 'MSMF' in backend:
            camprops.update(MSMF)
        else:
            camprops.update(V4L2)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)
        # self.setupCamProps()  # Load specific camera properties and apply to them to widgets
        self.camWorker = CamWorker()
        self.camThread = QThread(self)
        self.camWorker.moveToThread(self.camThread)
        self.camThread.start()
        self.camWorker.newFrame.connect(self.setImage)
        self.camStartSignal.connect(self.camWorker.startCam)
        self.camStopSignal.connect(self.camWorker.stopCam)
        self.camWorker.camStopped.connect(self.camStopped)
        self.new_image = False
        # self.updateProps()

    def initCV2(self):
        self.cv2Worker = CV2Worker()
        self.cv2Thread = QThread(self)
        self.cv2Worker.moveToThread(self.cv2Thread)
        self.cv2Thread.start()
        self.cv2Worker.cv2_ready.connect(self.cv2_ready_slot)
        self.cv2Worker.show_cv2.connect(self.procImage)
        self.find_well_signal.connect(self.cv2Worker.find_well)
        self.cv2_pass_frame_signal.connect(self.cv2Worker.pass_frame)
        self.cv2_pass_params_signal.connect(self.cv2Worker.pass_params)
        self.snap_reprocess_button.clicked.connect(self.cv2_reprocess)
        self.cv2_ready = True

    def initZbar(self):
        self.qrData = ''
        self.qrFile = None
        self.codeList = dict()
        self.plateList = dict()
        self.scans = 0
        self.qr_crop = 1/3
        self.qr_factor = 1
        self.qrWorker = ZbarWorker(crop=self.qr_crop, factor=self.qr_factor)
        self.qrThread = QThread(self)
        self.qrWorker.moveToThread(self.qrThread)
        self.qrThread.start()
        self.qrWorker.newScans.connect(self.updateScans)
        self.qrWorker.showCode.connect(self.procImage)
        self.qrWorker.qrReady.connect(self.qrReady)
        self.decodeQrSignal.connect(self.qrWorker.decodeQR)
        self.qr_ready = True
        print('QR reader initialized')

    def initOT2(self):
        self.plates_on_deck = None
        self.ot2_current_slot_item = None
        self.platesOnDeckTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.platesOnDeckTableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ot2Worker = OT2Worker()
        self.OT2Thread = QThread(self)
        self.ot2Worker.moveToThread(self.OT2Thread)
        self.OT2Thread.start()
        self.ot2Worker.ot2_connected.connect(self.ot2_connection_status)
        self.qrWorker.newScans.connect(self.ot2Worker.qr_scanned_slot)
        self.qrWorker.qrReady.connect(self.ot2Worker.qr_not_found_slot)
        self.ot2Worker.ot2_deck_scanned.connect(self.update_deck)
        self.ot2Worker.ot2_scan_qr.connect(self.scanQR)
        self.ot2ServerConnectPushButton.clicked.connect(self.ot2_connect)
        self.ot2_connect_signal.connect(self.ot2Worker._connect)
        self.ot2ServerDisconnectPushButton.clicked.connect(self.ot2Worker.disconnect)
        self.scanDeckPushButton.clicked.connect(self.ot2Worker.scan_plates)
        self.ot2SendCommandPushButton.clicked.connect(self.ot2_cmd)
        self.ot2_command_signal.connect(self.ot2Worker.cmd)
        self.ot2MoveCameraPushButton.clicked.connect(self.ot2_camera_to)
        self.ot2_cam_to_signal.connect(self.ot2Worker.cam_to)
        self.ot2HomePushButton.clicked.connect(self.ot2Worker.home)
        self.ot2LightsOnPushButton.clicked.connect(self.ot2_lights_on)
        self.ot2LightsOffPushButton.clicked.connect(self.ot2_lights_off)
        self.ot2ConnectRobotPushButton.clicked.connect(self.ot2Worker.ot2_connect)
        self.ot2Worker.ot2_slot_update_signal.connect(self.ot2_update_slot)
        self.ot2Worker.ot2_command_response.connect(print)
        self.ot2Worker.ot2_error.connect(self.ot2_error)
        print('OT-2 Commander initialized')

    def initDatabase(self):
        self.Stocks = OrderedDict()
        self.plate_manifest = None
        self.activeStock = None
        self.activeAnimal = None
        self.activeColony = None
        self.activeEvent = None
        self.last_selected_tree_item = None
        # event image display, choose from: 'before', 'after', 'stacked', 'side-by-side', 'overlay'
        self.event_image_display_approach = 'overlay'
        self.databasePixmap = QPixmap(':/HydraBot/Media/Hydra Fluor crop.jpg')
        #  Check for database and/or database settings
        #  Load database if applicable
        self.databaseTreeWidget.setStyleSheet("QTreeWidget::item {padding: 5px;}")
        self.databaseTreeWidget.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.databaseTreeWidget.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.databaseTreeWidget.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def cleanClose(self):
        print('Closing HydraBot')
        if self.cam is not None:
            print('Stopping Camera Thread')
            self.camStopSignal.emit()
            while self.cameraStopped is False:
                QCoreApplication.processEvents()
                QThread.msleep(10)
            self.camThread.quit()
            if self.camThread.wait(100) is False:
                print('Timed out waiting on Camera Thread')
        if self.qr_ready is False:
            print('Waiting on QR Thread')
        while self.qr_ready is False:
            QCoreApplication.processEvents()
            QThread.msleep(10)
        print('Stopping QR Thread')
        self.qrThread.quit()
        if self.qrThread.wait(1000) is False:
            print('Timed out waiting on QR Thread')
        print('Stopping CV2 Thread')
        self.cv2Thread.quit()
        if self.cv2Thread.wait(1000) is False:
            print('Timed out waiting on CV2 Thread')
        print('Stopping OT-2 Thread')
        self.OT2Thread.quit()
        if self.OT2Thread.wait(10000) is False:
            print('Timed out waiting on OT-2 Thread')
        print('Closed')
        self.close()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)  # gets defined in the UI file

        self.define_variables()  # Define otherwise unaffiliated app variables

        self.createWidgets()  # Create non-Creator widgets and set them up

        self.connectSignals()  # Make signal connections between widgets

        self.initCamera()  # Create camera and camera variables.  Make connections

        self.initZbar()  # Create QR code scanner and variables.  Make connections

        self.initCV2()  # Create CV2 image processor and variables.  Make connections

        self.initOT2()  # Create OT-2 Commander and variables.  Make connections

        if self.cam is not None:
            self.camStartSignal.emit(self.cam)  # Start the camera stream by emitting the signal

        self.initDatabase()  # Setup the animal stock database

        self.MainTabs.setCurrentIndex(0)  # Enforce the tab seen on opening to be the first tab

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
