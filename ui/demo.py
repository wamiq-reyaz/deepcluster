import sys
import random
from PySide2 import QtCore, QtWidgets, QtGui

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.message = 'I have been clicked {} times'
        self.counter = 0
        # ["Hallo Welt", "你好，世界", "Hei maailma",
        #     "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel(self.message.format(self.counter))
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.image_data = QtGui.QPixmap('bb.jpg') 
        self.image_box = QtWidgets.QLabel()
        self.image_box.setPixmap(self.image_data)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.image_box)
        self.setLayout(self.layout)

        self.button.clicked.connect(self.magic)

    def magic(self):
        self.counter += 1
        self.text.setText(self.message.format(self.counter))
        self.image_data = QtGui.QPixmap('bb.jpg')
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MyWidget()
    widget.show()

    sys.exit(app.exec_())