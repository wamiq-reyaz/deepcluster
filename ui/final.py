import argparse
import sys
import os 
from os.path import join as pjoin
import time
import random

import faiss
import numpy as np
from glob import glob
from PIL import Image
import pandas as pd


from matplotlib.backends.qt_compat import QtGui, QtCore, QtWidgets, is_pyqt5
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

parser.add_argument('--img_dir', help='The path to the actual dataset')
parser.add_argument('--csv', help='CSV containing the properties of the dataset')
parser.add_argument('--debug', action='store_true', default=False,
                    help='Turn on the debug mode (default: False)')
parser.add_argument('--weights', default=None,
                    help='The path to the model (default: None')



######################################################################
DARK_THEME = True

if DARK_THEME:
    plt.rcParams['figure.facecolor'] = 'black'


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

######################################################################

class ImagePane(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(ImagePane, self).__init__(parent)
        self.active_opacity = 1.0
        self.inactive_opacity = 0.8

    def hoverEnterEvent(self, event):
        print('aa')
        self.setOpacity(self.active_opacity)
        
    def hoverLeaveEvent(self, event):
        self.setOpacity(self.inactive_opacity)

class ImageGrid(QtWidgets.QGraphicsView):
    def __init__(self, 
                parent=None,
                size=(4,4)):
        super(ImageGrid, self).__init__()
        self.layout = QtWidgets.QGraphicsGridLayout()

        self.num_panes = size[0]*size[1]
        self.nrows = size[0]
        self.ncols = size[1]
        self.panes = {ii:ImagePane(self) for ii in range(self.num_panes)}
        self._scene = QtWidgets.QGraphicsScene(self)

        # print(self.panes)

        for ii in range(self.num_panes):
            grid = self._linear2grid(ii)
            row = grid[0]
            col = grid[1]
            _pane = self._scene.addWidget(self.panes[ii])
            print(type(_pane))
            self.layout.addItem(_pane, row, col)


        self._form = QtWidgets.QGraphicsWidget()
        self._form.setLayout(self.layout)
        self._scene.addItem(self._form)

        # pil_img = Image.open('/home/parawr/Projects/demo/PyQtImageViewer-master/icons/light/icon_default.png')
        pil_img = Image.open('/home/parawr/Desktop/clustering7k_4096dim.png')
        np_img = np.array(pil_img)
        # for _, pane in self.panes.items():
        self.panes[0].setPixmap(self.pixmapFromArray(np_img))

        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255))) #define dark gray background color
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def _linear2grid(self, idx):
        row = idx//self.ncols
        col = idx%self.nrows

        return (row, col)

    def _grid2linear(self, grid):
        row = grid[0]
        col = grid[1]

        return col + row*self.ncols

    def set_image(self, idxes, images):
        for idx, img in zip(idxes, images):
            self.panes[idx].setPixmap(img)
        return
    
    def pixmapFromArray(self, array):
        # self.imageShape = QSize(array.shape[1], array.shape[0])
        print('image shape: {}x{}'.format(array.shape[1], array.shape[0]))
        cp = array.copy()
        image = QtGui.QImage(cp, array.shape[1], array.shape[0], QtGui.QImage.Format_RGB888) #FIX this doesn't work for all images
        return QtGui.QPixmap(image)


class FacApp(QtWidgets.QMainWindow):
    def __init__(self, 
                args=None,
                parent=None):

        super(FacApp, self).__init__(parent)
        
        ## Layout and aesthetics
        self.n_cols = 4
        self.n_rows = 4
        self.n_subplots = self.n_cols * self.n_rows
        self.eps = 0.01
        self.weps = 0.01
        self.heps = 0.01

        self.text_resolution_h = 'Resolution H'
        self.text_resolution_v = 'Resolution V'
        self.text_num_floors = '#Floors'
        self.text_height = 'Height'
        self.text_occlusion = 'Occlusion%'
        self.text_blur = 'Blur'
        self.text_viewing_angle = 'Viewing Angle'
        self.text_number_windows = '#Windows'
        self.text_aspect_ratio = 'Aspect Ratio'

        #PANTONE 3553 C
        self.highlight_color = (0, 0.423, 0.690, 0.8)
        self.highlight_edge_color = (0, 0.423, 0.690, 1)

        if args.debug:
            print('Debug mode')
            self.image_list = None

        if args is not None:
            print('Loading images')
            self.img_dir = args.img_dir
            self.df = pd.read_csv(args.csv)
            self.image_names = self.df['name']

            # self.image_list = glob(os.path.join(args.img_dir, '*/*/*.jpg'))
            # self.image_list = self.image_list + glob(os.path.join(args.img_dir, '*/*.jpg'))
            self.num_images = len(self.image_names)

            print('Loaded {} images '.format(self.num_images))


        ######## Attach Model to the app #################

        ####### Set up the GUI ##################
        self.setWindowTitle('DeFeat GAX')
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


        #####################################################################################
        self.display_pane_layout = QtWidgets.QVBoxLayout(self.display_pane)
        self.aa = ImageGrid(size=(1,1))
        self.display_pane_layout.addWidget(self.aa)

        # Setup the display pane
        # self.display_pane_layout = QtWidgets.QVBoxLayout(self.display_pane)
        # self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        # self.display_pane_layout.addWidget(self.canvas)
        # self.addToolBar(NavigationToolbar(self.canvas, self.display_pane))

        # self.axes = self.canvas.figure.subplots(self.n_rows, self.n_cols, sharex=True)
        # self.axes_list = list(self.axes.ravel())
        # self.clean_layout()
        # self.canvas.draw()
        # self.backgrounds = [self.canvas.copy_from_bbox(ax.bbox) for ax in self.axes.ravel()]
        # self.artists = []
        # self.indices = []
        # self.active_axis = None
        # self.patches = []
        # self.gen_patches()
        # self.canvas.mpl_connect('button_press_event', self.on_click)
        # self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        # self.canvas.mpl_connect('resize_event', self.on_resize)


        ## The Hover pane
        self.hover_pane_layout = QtWidgets.QVBoxLayout(self.hover_pane)
        self.hover_pane_layout.addWidget(QtWidgets.QWidget())


        ## The home for all the sliders
        self.slider_pane_layout = QtWidgets.QVBoxLayout(self.slider_pane)
        self.slider1 =  MinMax(self.slider_pane)
        self.slider1.set_name(self.text_resolution_h)
        self.slider_pane_layout.addWidget(self.slider1)

        self.slider2 =  MinMax(self.slider_pane)
        self.slider2.set_name(self.text_resolution_v)
        self.slider_pane_layout.addWidget(self.slider2)

        self.slider3 =  MinMax(self.slider_pane)
        self.slider3.set_name(self.text_num_floors)
        self.slider_pane_layout.addWidget(self.slider3)

        self.slider4 =  MinMax(self.slider_pane)
        self.slider4.set_name(self.text_height)
        self.slider_pane_layout.addWidget(self.slider4)

        self.slider5 =  MinMax(self.slider_pane)
        self.slider5.set_name(self.text_occlusion)
        self.slider_pane_layout.addWidget(self.slider5)

        self.slider6 =  MinMax(self.slider_pane)
        self.slider6.set_name(self.text_blur)
        self.slider_pane_layout.addWidget(self.slider6)

        self.slider7 =  MinMax(self.slider_pane)
        self.slider7.set_name(self.text_viewing_angle)
        self.slider_pane_layout.addWidget(self.slider7)

        self.slider8 =  MinMax(self.slider_pane)
        self.slider8.set_name(self.text_number_windows)
        self.slider_pane_layout.addWidget(self.slider8)

        self.slider9 =  MinMax(self.slider_pane)
        self.slider9.set_name(self.text_aspect_ratio)
        self.slider_pane_layout.addWidget(self.slider9)

        

        self.connect_sliders()

        ## Set up the buttons in the search pane
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

        self.toolButton_search_image = QtWidgets.QToolButton(self.search_pane)
        self.toolButton_search_image.setGeometry(QtCore.QRect(0, 0, 730, 110))
        self.toolButton_search_image.setMinimumSize(QtCore.QSize(800, 50))
        self.toolButton_search_image.setText('Search')
        self.toolButton_search_image.clicked.connect(self.search)

        self.toolButton_load_image = QtWidgets.QToolButton(self.search_pane)
        self.toolButton_load_image.setGeometry(QtCore.QRect(0, 0, 730, 110))
        self.toolButton_load_image.setMinimumSize(QtCore.QSize(800, 50))
        self.toolButton_load_image.setText('Load Image')
        self.toolButton_load_image.clicked.connect(self.load_images)

        self.search_pane_layout.addWidget(self.horiz_widget)
        self.search_pane_layout.addWidget(self.toolButton_search_image)
        self.search_pane_layout.addWidget(self.toolButton_load_image)

        elements_to_magnify = ['radioButton_facade', 'radioButton_window',
                               'radioButton_city', 'toolButton_load_image',
                               'toolButton_search_image']
        self.magnify_font(elements_to_magnify)


    def create_image(self, idx):
        pass

    def magnify_font(self, elements):
        font = QtGui.QFont()
        font.setPointSize(15)
        for e in elements:
            curr_elem = getattr(self, e)
            curr_elem.setFont(font)

    def connect_sliders(self):
        for ii in range(7):
            slider_string = 'slider' + str(ii+1)
            curr_slider = getattr(self, slider_string)
            curr_slider.changed.connect(self.on_slider_change)

    def load_images(self):
        self.artists = []
        end = time.time()
        self.idx = np.random.randint(0, self.num_images, self.n_subplots)
        # idx = list(idx)

        for i, ax in enumerate(self.axes.ravel()):
            name = pjoin(self.img_dir,self.image_names[self.idx[i]])
            with Image.open(name) as img:
                # ax.clear()
                _img = ax.imshow(img, zorder=-1)
                self.artists.append(_img)
                ax.draw_artist(_img)

        
        self.canvas.update()
        self.canvas.flush_events()
        self.clean_layout()
        self.update_patches()
        print(time.time() - end)

    def search(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a file')
        # detect which switch is on

        # compute the features

        # perform the lookup in the appropriate space (facade/windows)

        # update the display
        #TODO
        pass

    def on_slider_change(self, which):
        print(which)
        
    def clean_layout(self):
        self.canvas.figure.tight_layout()
        self.canvas.figure.subplots_adjust(left=self.eps,
                                           bottom=self.eps,
                                           right=1-self.eps,
                                           top=1-self.eps,
                                           wspace=self.weps,
                                           hspace=self.heps)
        for ax in self.axes.ravel():
            ax.axis('off')

    def gen_patches(self):
        for i, ax in enumerate(self.axes_list):
            curr_bbox = quad_from_ax(ax)
            props = dict(visible=False,
                         facecolor=self.highlight_color,
                         edgecolor=self.highlight_edge_color,
                         linewidth=6, zorder=1)
            p = Polygon(curr_bbox, **props)

            self.patches.append(ax.add_patch(p))
            ax.draw_artist(self.patches[i])

        return


    def on_click(self, event):
        idx = self.axes_list.index(event.inaxes)
        print(self.image_names[self.idx[idx]])

    def on_resize(self, event):
        pass

    def update_patches(self):
        # ensure that the poylgons are stretched to the new axis size
        for i, ax in enumerate(self.axes_list):
            curr_bbox = quad_from_ax(ax)
            patch = ax.patches[0]
            patch.set_xy(curr_bbox)

        # for i, ax in enumerate(self.axes_list):
        #     patch = ax.patches[0]
        #     print(patch.get_xy())
        # return

    def on_hover(self, event):
        # Four cases 
        # None to Axis
        if self.active_axis is None and event.inaxes:
            # Find the inaxes index
            idx = self.axes_list.index(event.inaxes)
            curr_axis = self.axes_list[idx]

            # set active axis to hovered axis
            self.active_axis = curr_axis

            # set patch visiblity
            curr_axis.patches[0].set_visible(True)
            curr_axis.draw_artist(curr_axis.patches[0])

        # Axis to None
        elif event.inaxes is None and self.active_axis:
            # Find the axis again
            idx = self.axes_list.index(self.active_axis)
            curr_axis = self.axes_list[idx]

            # Now active axis is None
            self.active_axis = None

            # We are going out of active region and need to remove highlight
            curr_axis.patches[0].set_visible(False)
            curr_axis.draw_artist(curr_axis.patches[0])

        # Axis to Axis
        elif event.inaxes == self.active_axis:
            return

        # Axis1 to Axis2
        elif event.inaxes and self.active_axis:
            idx = self.axes_list.index(event.inaxes)
            curr_axis = self.axes_list[idx]

            active_idx = self.axes_list.index(self.active_axis)
            active_axis = self.axes_list[active_idx]

            # We are going out of active region and need to remove highlight
            active_axis.patches[0].set_visible(False)
            active_axis.draw_artist(active_axis.patches[0])

            # Also need to highlight the new axis
            curr_axis.patches[0].set_visible(True)
            curr_axis.draw_artist(curr_axis.patches[0])
            self.active_axis = curr_axis

        else:
            raise ValueError('This should never have happened')

        self.canvas.update()
        self.canvas.flush_events()


def main(args):
    qapp = QtWidgets.QApplication(sys.argv)
    app = FacApp(args)
    
    #setup the stylesheet
    if DARK_THEME:
        import qdarkstyle
        qapp.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    app.show()
    qapp.exec_()

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)