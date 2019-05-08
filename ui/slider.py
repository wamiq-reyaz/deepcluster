import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class ScrollableWindow(QtWidgets.QMainWindow):
    def __init__(self, fig):
        self.qapp = QtWidgets.QApplication([])

        QtWidgets.QMainWindow.__init__(self)
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)

        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.canvas.mpl_connect("scroll_event", self.scrolling)
        self.canvas.mpl_connect('button_press_event', self.onclick)

        self.show()
        exit(self.qapp.exec_())

    def scrolling(self, event):
        val = self.scroll.verticalScrollBar().value()
        if event.button =="down":
            self.scroll.verticalScrollBar().setValue(val+100)
        else:
            self.scroll.verticalScrollBar().setValue(val-100)

    def onclick(self, event):
        print(event.x, event.y, event.inaxes, event.xdata, event.ydata)
        event.inaxes.clear()
        event.inaxes.figure.canvas.draw()

# create a figure and some subplots
fig, axes = plt.subplots(ncols=4, nrows=5, figsize=(16,16))
fig.tight_layout()
for ax in axes.flatten():
    ax.plot([2,3,5,1])
    ax.axis('off')


# pass the figure to the custom window
a = ScrollableWindow(fig)