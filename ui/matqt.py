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

def gen_two_clusters(num_elem):
    points = np.random.rand(num_elem, 2)
    points = np.vstack([points, 2+np.random.rand(num_elem, 2)])
    return points

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)


        self.line = QtWidgets.QFrame(self._main)
        # self.line.setGeometry(QtCore.QRect(1990, -20, 20, 1491))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.frame = QtWidgets.QFrame(self._main)
        # self.frame.setGeometry(QtCore.QRect(59, 39, 1891, 971))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.pushButton_switch_view = QtWidgets.QPushButton(self._main)
        # self.pushButton_switch_view.setGeometry(QtCore.QRect(10, 40, 51, 211))
        self.pushButton_switch_view.setObjectName("pushButton_switch_view")

        layout = QtWidgets.QVBoxLayout(self._main)

        self.reload_button = QtWidgets.QToolButton(self)
        self.reload_button.setText('Reload scatter plot')
        self.reload_button.clicked.connect(self._update_scatter)
        self.num_clusterings = 10
        self.curr_clustering = 0
        self.points = [gen_two_clusters(100000) for ii in range(self.num_clusterings)]
        layout.addWidget(self.reload_button)

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(static_canvas)
        self.addToolBar(NavigationToolbar(static_canvas, self))

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(dynamic_canvas, self))

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")
        self._static_ax.set_title('Scatter Plot')

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(
            100, [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        pass
        # self._dynamic_ax.clear()
        # t = np.linspace(0, 10, 101)
        # # Shift the sinusoid as a function of time.
        # self._dynamic_ax.plot(t, np.sin(t + time.time()))
        # self._dynamic_ax.figure.canvas.draw()

    def _update_scatter(self):
        self._static_ax.clear()
        # print(self.points)
        number = np.random.randint(100000)
        xx = self.points[self.curr_clustering][number:int(number*1.4), 0]
        yy = self.points[self.curr_clustering][number:int(number*1.4), 1]
        self._static_ax.scatter(xx, yy, alpha=0.8)
        self._static_ax.figure.canvas.draw()
        self.curr_clustering += 1


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()