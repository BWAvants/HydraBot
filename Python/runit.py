# always seem to need this
import sys
# from time import sleep
import cv2
from numpy import ndarray

# This gets the Qt stuff
# import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, QThread

# This is our window from QtCreator
import mainwindow_auto
import media


def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug


class CamThread(QThread):
    # changePixmap = pyqtSignal(QImage)
    changePixmap = pyqtSignal(ndarray)

    def run(self):
        cam = cv2.VideoCapture(0)
        print(cam.getBackendName())
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        while cam.isOpened():
            check, frame = cam.read()
            if check is True:
                # print('frame grabbed')
                # rgbImg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # height, width, channel = rgbImg.shape
                # bytesPerLine = 3 * width
                # qImg = QImage(rgbImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
                # self.changePixmap.emit(qImg)
                self.changePixmap.emit(frame)
                # self.msleep(30)
            else:
                self.msleep(3)
        print('Camera Closed')


# create class for our Raspberry Pi GUI
class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
    # access variables inside of the UI's file

    def setImagae(self, image):
        if image is None:
            return
        rgbImg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if self.cam_width is None:
            self.cam_height, self.cam_width, channel = rgbImg.shape
            self.cam_bytes_per_line = 3 * self.cam_width
            print((self.cam_width, self.cam_height))
        #qImg = QImage(rgbImg.data, self.cam_width, self.cam_height, self.cam_bytes_per_line, QImage.Format_RGB888)
        #pMap = QPixmap.fromImage(qImg)
        pMap = QPixmap.fromImage(
            QImage(rgbImg.data, self.cam_width, self.cam_height, self.cam_bytes_per_line, QImage.Format_RGB888)
        )
        self.labelCamera1.setPixmap(pMap)

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)  # gets defined in the UI file
        self.cam_width = None
        self.cam_height = None
        self.cam_bytes_per_line = None
        th = CamThread(self)
        th.changePixmap.connect(self.setImagae)
        th.start()


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
