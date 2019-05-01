from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

class MinMaxSlider(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QHBoxLayout(self)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.min_label_widget = QtWidgets.QWidget()
        min_label_widget_layout = QtWidgets.QVBoxLayout(self.min_label_widget)

        self.min_label_value = QtWidgets.QLineEdit(self.min_label_widget)
        self.min_label = QtWidgets.QLabel(self.min_label_widget)
        self.min_label.setAlignment(QtCore.Qt.AlignCenter)
        self.min_label.setText('Min.')

        min_label_widget_layout.addWidget(self.min_label)
        min_label_widget_layout.addWidget(self.min_label_value)
    
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")

        self.max_label_widget = QtWidgets.QWidget()
        max_label_widget_layout = QtWidgets.QVBoxLayout(self.max_label_widget)

        self.max_label_value = QtWidgets.QLineEdit(self.max_label_widget)
        self.max_label = QtWidgets.QLabel(self.max_label_widget)
        self.max_label.setAlignment(QtCore.Qt.AlignCenter)
        self.max_label.setText('Max.')

        max_label_widget_layout.addWidget(self.max_label)
        max_label_widget_layout.addWidget(self.max_label_value)


        layout.addWidget(self.label)
        layout.addWidget(self.line)
        layout.addWidget(self.min_label_widget)
        layout.addWidget(self.slider)
        layout.addWidget(self.max_label_widget)
        self.setLayout(layout)

    def magic(self):
        pass