import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.style.use('seaborn') 

from glob import glob
from PIL import Image
import random

import interface

class FacApp(QtWidgets.QMainWindow, interface.Ui_MainWindow):
    def __init__(self, parent=None):
        super(FacApp, self).__init__(parent)
        self.setupUi(self)

        self.horizontalSlider_3.setMouseTracking(True)
        self.horizontalSlider_3.valueChanged.connect(self.boing)

        self.page.mpl_connect('button_press_event', self.onclick)

        self.image_list = glob('/home/parawr/Projects/clusterFacadeData/*/*.jpg')
        self.num_images = len(self.image_list)
        self.counter = random.randint(0, self.num_images)

    def boing(self):
        print(self.horizontalSlider_3.value())

    def onclick(self, event):
        self._timer.stop()
        print(event.x, event.y, event.inaxes, event.xdata, event.ydata)
        img = Image.open(self.image_list[self.counter])
        self._static_ax.imshow(img)
        self._static_ax.figure.canvas.draw()
        self._static_ax.set_xticks([])
        self._static_ax.set_yticks([])
        self.counter = (self.counter + 1) % self.num_images
        # self._timer.start()

def main():
    qapp = QtWidgets.QApplication(sys.argv)
    app = FacApp()
    app.show()
    qapp.exec_()

if __name__ == "__main__":
    main()