import argparse
import sys
import os 
import time
import random


import numpy as np
from glob import glob
from PIL import Image



from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from matplotlib.patches import Polygon
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.style.use('seaborn') 

from minmax import MinMax


######################################################################
parser = argparse.ArgumentParser(description='UI for large scale data-guided asset extraction')

parser.add_argument('--img_dir', help='path to dataset')


def quad_from_ax(ax):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # print(xlim, ylim)
    base = np.array([xlim[0], ylim[0]])
    # print(base)
    width = np.array([xlim[1], 0])
    height = np.array([0, ylim[1]])
    quad_points = np.vstack([base, base+height, (base+height)+width, base+width])
    return quad_points

class FacApp(QtWidgets.QMainWindow):
    def __init__(self, 
                args=None,
                parent=None):

        super(FacApp, self).__init__(parent)
        
        self.n_cols = 4
        self.n_rows = 4
        self.n_subplots = self.n_cols * self.n_rows

        if args is not None:
            print('Loading images')
            self.image_list = glob(os.path.join(args.img_dir, '*/*/*.jpg'))
            self.image_list = self.image_list + glob(os.path.join(args.img_dir, '*/*.jpg'))
            self.num_images = len(self.image_list)
            print('Loaded {} images '.format(self.num_images))

        # self.resize(1080,1080)
        self.setWindowTitle('FeaGax')
        self.centralwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        self.display_pane = QtWidgets.QWidget(self.centralwidget)
        self.slider_pane = QtWidgets.QWidget(self.centralwidget)
        self.hover_pane = QtWidgets.QWidget(self.centralwidget)
        self.search_pane = QtWidgets.QWidget(self.centralwidget)

        self.gridLayout.addWidget(self.slider_pane, 0, 3, 3, 1)
        self.gridLayout.addWidget(self.display_pane, 0, 0, 3, 3)
        self.gridLayout.addWidget(self.hover_pane, 3, 0, 1, 3)
        self.gridLayout.addWidget(self.search_pane, 3, 3, 1, 1)

        self.display_pane_layout = QtWidgets.QVBoxLayout(self.display_pane)
        self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.display_pane_layout.addWidget(self.canvas)
        self.addToolBar(NavigationToolbar(self.canvas, self.display_pane))

        self.axes = self.canvas.figure.subplots(self.n_rows, self.n_cols, sharex=True)
        self.axes_list = list(self.axes.ravel())
        self.clean_layout()
        self.canvas.draw()
        self.backgrounds = [self.canvas.copy_from_bbox(ax.bbox) for ax in self.axes.ravel()]
        self.artists = []
        self.indices = []
        self.active_axis = None
        self.patches = []
        self.gen_patches()
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        # self.artists = [self.canvas.copy_from_bbox(ax.bbox) for ax in self.axes.ravel()]


        self.hover_pane_layout = QtWidgets.QVBoxLayout(self.hover_pane)
        self.hover_pane_layout.addWidget(QtWidgets.QWidget())

        self.slider_pane_layout = QtWidgets.QVBoxLayout(self.slider_pane)
        self.slider1 =  MinMax(self.slider_pane)
        self.slider1.set_name('Resolution H')
        self.slider_pane_layout.addWidget(self.slider1)

        self.slider2 =  MinMax(self.slider_pane)
        self.slider2.set_name('Resolution V')
        self.slider_pane_layout.addWidget(self.slider2)

        self.slider3 =  MinMax(self.slider_pane)
        self.slider3.set_name('#Floors')
        self.slider_pane_layout.addWidget(self.slider3)

        self.slider4 =  MinMax(self.slider_pane)
        self.slider4.set_name('Height')
        self.slider_pane_layout.addWidget(self.slider4)

        self.slider5 =  MinMax(self.slider_pane)
        self.slider5.set_name('Occlusion%')
        self.slider_pane_layout.addWidget(self.slider5)

        self.slider6 =  MinMax(self.slider_pane)
        self.slider6.set_name('Blur')
        self.slider_pane_layout.addWidget(self.slider6)


        self.slider7 =  MinMax(self.slider_pane)
        self.slider_pane_layout.addWidget(self.slider7)

        self.connect_sliders()

        self.search_pane_layout = QtWidgets.QVBoxLayout(self.search_pane)
        self.horiz_widget = QtWidgets.QWidget(self.search_pane)

        self.horiz_widget_layout = QtWidgets.QHBoxLayout(self.horiz_widget)
        self.horiz_widget_layout.setGeometry(QtCore.QRect(0, 0, 500, 50))

        self.radioButton_facade = QtWidgets.QRadioButton(self.horiz_widget)
        self.radioButton_facade.setText('Facade')
        self.horiz_widget_layout.addWidget(self.radioButton_facade)

        self.radioButton_window = QtWidgets.QRadioButton(self.horiz_widget)
        self.radioButton_window.setText('Window')
        self.horiz_widget_layout.addWidget(self.radioButton_window)

        self.radioButton_city = QtWidgets.QRadioButton(self.horiz_widget)
        self.radioButton_city.setText('City')
        self.horiz_widget_layout.addWidget(self.radioButton_city)

        self.toolButton_load_image = QtWidgets.QToolButton(self.search_pane)
        self.toolButton_load_image.clicked.connect(self.load_images)


        self.search_pane_layout.addWidget(self.horiz_widget)
        self.search_pane_layout.addWidget(self.toolButton_load_image)


    def connect_sliders(self):
        for ii in range(7):
            slider_string = 'slider' + str(ii+1)
            curr_slider = getattr(self, slider_string)
            curr_slider.changed.connect(self.on_slider_change)

    def on_slider_change(self):
        print('changed')

    def load_images(self):
        self.artists = []
        end = time.time()
        self.idx = np.random.randint(0, self.num_images, self.n_subplots)
        # idx = list(idx)
        for i, ax in enumerate(self.axes.ravel()):
            name = self.image_list[self.idx[i]]
            with Image.open(name) as img:
                # ax.clear()
                _img = ax.imshow(img, zorder=-1)
                self.artists.append(_img)
                ax.draw_artist(_img)
                # print(_img.zorder)
                
        # print('display')
        self.clean_layout()
        self.canvas.update()
        self.canvas.flush_events()
        print(time.time() - end)
        
    def clean_layout(self):
        self.canvas.figure.tight_layout()
        self.canvas.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        for ax in self.axes.ravel():
            ax.axis('off')

    def gen_patches(self):
        for i, ax in enumerate(self.axes_list):
            curr_bbox = quad_from_ax(ax)
            props = dict(visible=False, facecolor=(0, 0, 1, 0.4), edgecolor=(0, 0, 1), linewidth=2, zorder=1)
            p = Polygon(curr_bbox, **props)

            self.patches.append(ax.add_patch(p))
            ax.draw_artist(self.patches[i])

        return

    def on_click(self, event):
        idx = self.axes_list.index(event.inaxes)
        print(self.image_list[self.idx[idx]])

    def on_hover(self, event):
        if event.inaxes is None:
            return

        idx = self.axes_list.index(event.inaxes)
        curr_axis = self.axes_list[idx]
        curr_img = self.artists[idx]

        print(curr_axis.patches)
        curr_axis.patches[0].set_visible(True)
        curr_axis.draw_artist(curr_img)
        curr_axis.draw_artist(curr_axis.patches[0])
        self.clean_layout()
        self.canvas.draw()
        self.canvas.flush_events()

        # if curr_axis is not None and idx != self.active_axis:
        #     if self.active_axis is not None and len(self.axes_list[self.active_axis].patches) > 1:
        #         self.axes_list[self.active_axis].patches[0].set_visible(False)
        #         print(self.active_axis)
        #     self.active_axis = idx
        #     curr_bbox = quad_from_ax(curr_axis)
        #     props = dict(visible=True, facecolor=(0, 0, 1, 0.4), edgecolor=(0, 0, 1), linewidth=2)
        #     p = Polygon(curr_bbox, **props)

        #     _patch = curr_axis.add_patch(p)
        #     curr_axis.draw_artist(_patch)
        #     print(_patch.zorder)
        #     self.canvas.update()
        #     self.canvas.flush_events()
        # elif curr_axis is None:
        #     self.active_axis = None

def main(args):
    qapp = QtWidgets.QApplication(sys.argv)
    app = FacApp(args)
    app.show()
    qapp.exec_()

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)