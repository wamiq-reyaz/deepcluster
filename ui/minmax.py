import sys
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from min_max_slider import Ui_Form

class MinMax(QtWidgets.QWidget):
    changed = QtCore.Signal(str, float, float)
    def __init__(self, parent=None):
        super(MinMax, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout() 
        self.setLayout(self.layout)

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.difference = 5

        self.actual_min = 0
        self.actual_max = 0
        self.range = 0
        self.set_limits(0, 100)

        self.curr_min = self.ui.min_slider.value()
        self.curr_max = self.ui.max_slider.value()
        self.update_text()
        
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
        _min, _max = self._value()
        self.changed.emit(self.ui.label.text(), _min, _max )

    def update_max(self):
        curr_min = self.ui.min_slider.value()
        curr_max = self.ui.max_slider.value()

        if curr_min > curr_max - self.difference:
            self.ui.min_slider.blockSignals(True)
            self.ui.min_slider.setValue(curr_max-self.difference)
            self.ui.min_slider.blockSignals(False)
        self.update_text()   
        _min, _max = self._value()
        self.changed.emit(self.ui.label.text(), _min, _max)

    def update_text(self):
        _min, _max = self._value()
        self.ui.min_text.setText('{:.2f}'.format(_min))
        self.ui.max_text.setText('{:.2f}'.format(_max))

    def set_limits(self, _min, _max):
        self.actual_min = _min
        self.actual_max = _max
        self.range = self.actual_max - self.actual_min
        self.update_text()   

    def _value(self):
        _min = self.actual_min + (self.range * self.ui.min_slider.value() / 100.0)
        _max = self.actual_min + (self.range * self.ui.max_slider.value() / 100.0)

        return _min, _max

def signal_handle(name, _min, _max):
    pass
    # print(name, _min, _max)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MinMax()
    widget.changed.connect(signal_handle)
    widget.set_name('asf')
    widget.show()

    sys.exit(app.exec_())