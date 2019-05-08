import sys
import random
from PySide2 import QtCore, QtWidgets, QtGui
from min_max_slider import Ui_Form

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)


        self.widget2 = QtWidgets.QWidget(self.widget)
        self.widget2.ui = Ui_Form()
        self.widget2.ui.setupUi(self.widget2)

        self.widget.layout().addWidget(self.widget2)

        self.widget3 = QtWidgets.QWidget(self.widget)
        self.widget3.ui = Ui_Form()
        self.widget3.ui.setupUi(self.widget3)

        self.widget.layout().addWidget(self.widget3)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MainWindow()
    widget.show()

    sys.exit(app.exec_())