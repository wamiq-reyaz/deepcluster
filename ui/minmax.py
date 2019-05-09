import sys
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from min_max_slider import Ui_Form

class MinMax(QtWidgets.QWidget):
    changed = QtCore.Signal(str)
    def __init__(self, parent=None):
        super(MinMax, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout() 
        self.setLayout(self.layout)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.curr_min = self.ui.min_slider.value()
        self.curr_max = self.ui.max_slider.value()
        self.ui.min_text.setText(str(self.curr_min))
        self.ui.max_text.setText(str(self.curr_max))

        self.difference = 5
        
        self.ui.max_slider.valueChanged.connect(self.update_max)
        self.ui.min_slider.valueChanged.connect(self.update_min)
        

    def set_name(self, name):
        self.ui.label.setText(name)

    def update_min(self):
        curr_min = self.ui.min_slider.value()
        curr_max = self.ui.max_slider.value()

        if curr_max < curr_min + self.difference:
            self.ui.max_slider.blockSignals(True)
            self.ui.max_slider.setValue(curr_min+self.difference)
            self.ui.max_slider.blockSignals(False)
        self.update_text()
        self.changed.emit(self.ui.label.text() + '_min')

    def update_max(self):
        curr_min = self.ui.min_slider.value()
        curr_max = self.ui.max_slider.value()

        if curr_min > curr_max - self.difference:
            self.ui.min_slider.blockSignals(True)
            self.ui.min_slider.setValue(curr_max-self.difference)
            self.ui.min_slider.blockSignals(False)
        self.update_text()        
        self.changed.emit(self.ui.label.text() + '_max')

    def update_text(self):
        self.ui.min_text.setText(str(self.ui.min_slider.value()))
        self.ui.max_text.setText(str(self.ui.max_slider.value()))


def signal_handle(signal):
    print(signal)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MinMax()
    widget.signal.connect(signal_handle)
    widget.set_name('asf')
    widget.show()

    sys.exit(app.exec_())