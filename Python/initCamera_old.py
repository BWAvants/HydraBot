# This is a snippet of the camera init script from hydrabot.py that is no longer used, preserved as a reference
# There are also included variable definitions and such preceding the init snippet


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


camStartSignal = pyqtSignal(cv2.VideoCapture, name='camStartSignal')
camStopSignal = pyqtSignal(name='camStopSignal')

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

def connectSignals(self):
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
    self.setButton.clicked.connect(self.genSetCamProp)
    self.getButton.clicked.connect(self.genGetCamProp)

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
    self.cameraStopped = False
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
    self.camThread = QThread(self)
    self.camWorker.moveToThread(self.camThread)
    self.camThread.start()
    self.camWorker.newFrame.connect(self.setImage)
    self.camStartSignal.connect(self.camWorker.startCam)
    self.camStopSignal.connect(self.camWorker.stopCam)
    self.camWorker.camStopped.connect(self.camStopped)
    self.updateProps()

def cleanClose(self):
    print('Stopping Camera Thread')
    self.camStopSignal.emit()
    while self.cameraStopped is False:
        QCoreApplication.processEvents()
        QThread.msleep(10)
    self.camThread.quit()
    if self.camThread.wait(100) is False:
        print('Timed out waiting on Camera Thread')