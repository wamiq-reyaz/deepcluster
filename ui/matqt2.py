import sys
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random

from utils import MinMaxSlider

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.workAreaLayout = QtWidgets.QHBoxLayout(self.centralwidget)

        self.pushButton_switch_view = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_switch_view.setObjectName("pushButton_switch_view")
        self.workAreaLayout.addWidget(self.pushButton_switch_view)

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.workAreaLayout.addWidget(self.frame)

        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.workAreaLayout.addWidget(self.line)

        self.verticalScrollBar = QtWidgets.QScrollBar(self.centralwidget)
        self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
        self.verticalScrollBar.setObjectName("verticalScrollBar")
        self.workAreaLayout.addWidget(self.verticalScrollBar)

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalSlider_resolution_v = MinMaxSlider()
        self.horizontalSlider_resolution_v.setObjectName("horizontalSlider_resolution_v")
        self.verticalLayout.addWidget(self.horizontalSlider_resolution_v)

        self.horizontalSlider_resolution_h = MinMaxSlider()
        self.horizontalSlider_resolution_h.setObjectName("horizontalSlider_resolution_h")
        self.verticalLayout.addWidget(self.horizontalSlider_resolution_h)

        self.horizontalSlider_height = MinMaxSlider()
        self.horizontalSlider_height.setObjectName("horizontalSlider_height")
        self.verticalLayout.addWidget(self.horizontalSlider_height)

        self.horizontalSlider_bluriness = MinMaxSlider()
        self.horizontalSlider_bluriness.setObjectName("horizontalSlider_bluriness")
        self.verticalLayout.addWidget(self.horizontalSlider_bluriness)

        self.horizontalSlider_obstruction = MinMaxSlider()
        self.horizontalSlider_obstruction.setObjectName("horizontalSlider_obstruction")
        self.verticalLayout.addWidget(self.horizontalSlider_obstruction)

        self.horizontalSlider_windows = MinMaxSlider()
        self.horizontalSlider_windows.setObjectName("horizontalSlider_windows")
        self.verticalLayout.addWidget(self.horizontalSlider_windows)

        self.horizontalSlider_windows_floor = MinMaxSlider()
        self.horizontalSlider_windows_floor.setObjectName("horizontalSlider_windows_floor")
        self.verticalLayout.addWidget(self.horizontalSlider_windows_floor)

        self.workAreaLayout.addWidget(self.verticalLayoutWidget)

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.radioButton_facade = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_facade.setObjectName("radioButton_facade")
        self.horizontalLayout.addWidget(self.radioButton_facade)

        self.radioButton_window = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_window.setObjectName("radioButton_window")
        self.horizontalLayout.addWidget(self.radioButton_window)

        self.radioButton_city = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioButton_city.setObjectName("radioButton_city")
        self.horizontalLayout.addWidget(self.radioButton_city)

        self.toolButton_load_image = QtWidgets.QToolButton(self.horizontalLayoutWidget)
        self.toolButton_load_image.setObjectName("toolButton_load_image")
        self.textEdit = QtWidgets.QTextEdit(self.horizontalLayoutWidget)
        self.textEdit.setObjectName("textEdit")


        self.workAreaLayout.addWidget(self.horizontalLayoutWidget)

        self.line.raise_()
        self.pushButton_switch_view.raise_()
        self.verticalScrollBar.raise_()
        self.verticalLayoutWidget.raise_()
        self.horizontalLayoutWidget.raise_()
        self.toolButton_load_image.raise_()
        self.textEdit.raise_()
        # self.verticalLayoutWidget_2.raise_()
        self.frame.raise_()
        # self.label_image_frame.raise_()
        # MainWindow.setCentralWidget(self.centralwidget)
        # self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 2547, 28))
        # self.menubar.setObjectName("menubar")
        # MainWindow.setMenuBar(self.menubar)
        # self.statusbar = QtWidgets.QStatusBar(MainWindow)
        # self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)


        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtWidgets.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        self.slider = MinMaxSlider()
        self.slider.label.setText('Resolution')

        # set the layout
        # layout = QtWidgets.QVBoxLayout(self.centralwidget)
        # layout.addWidget(self.toolbar)
        # layout.addWidget(self.canvas)
        # layout.addWidget(self.button)
        # layout.addWidget(self.slider)
        # self.setLayout(layout)

    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())