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

import interface

class FacApp(QtWidgets.QMainWindow, interface.Ui_MainWindow):
    def __init__(self, parent=None):
        super(FacApp, self).__init__(parent)
        self.setupUi(self)

        # print(self.page)
        # self.page = FigureCanvas(Figure(figsize=(5, 3)))
        # print(self.page)
        # self._static_ax = self.page.figure.subplots()
        # t = np.linspace(0, 10, 501)
        # self._static_ax.plot(t, np.tan(t), ".")
        # self._static_ax.set_title('Scatter Plot')

        # self.stackedWidget.addWidget(self.page)
        # self.gridLayout_4.addWidget(self.stackedWidget, 0, 0, 9, 1)
        # print(self)
        # self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)
        # self.gridLayout.addLayout(self.gridLayout_2, 5, 0, 1, 1)
        # MainWindow.setCentralWidget(self.centralwidget)

def main():
    qapp = QtWidgets.QApplication(sys.argv)
    app = FacApp()
    app.show()
    qapp.exec_()

if __name__ == "__main__":
    main()