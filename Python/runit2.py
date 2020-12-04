# always seem to need this
import sys
# from time import sleep
import cv2

# This gets the Qt stuff
# import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QCamera
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, QThread

# This is our window from QtCreator
import camtest_auto
import media


def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug


class CamThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cam = cv2.VideoCapture(0)
        print(cam.getBackendName())
        counter = 0
        while cam.isOpened():
            check, frame = cam.read()
            if check is True:
                # print('frame grabbed')
                rgbImg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = rgbImg.shape
                bytesPerLine = 3 * width
                qImg = QImage(rgbImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
                counter = (counter+1) % 300
                self.changePixmap.emit(qImg)
                self.msleep(30)
            else:
                self.msleep(3)
            if counter == 0:
                cam.release()
                cam = cv2.VideoCapture(0)
        print('Camera Closed')


# create class for our Raspberry Pi GUI
class MainWindow(QMainWindow, camtest_auto.Ui_MainWindow):
    # access variables inside of the UI's file

    def setImagae(self, image):
        if not image:
            return
        pMap = QPixmap.fromImage(image)
        self.labelCamera1.setPixmap(pMap)

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)  # gets defined in the UI file
        # th = CamThread(self)
        # th.changePixmap.connect(self.setImagae)
        # th.start()
        self.cam = QCamera()
        self.cam.setViewfinder(self.widget)
        self.cam.start()


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
