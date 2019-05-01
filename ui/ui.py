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

import layout

class FacApp(QtWidgets.QMainWindow, layout.Ui_MainWindow):
    def __init__(self, parent=None):
        super(FacApp, self).__init__(parent)
        self.setupUi(self)

def main():
    qapp = QtWidgets.QApplication(sys.argv)
    app = FacApp()
    app.show()
    qapp.exec_()

if __name__ == "__main__":
    main()