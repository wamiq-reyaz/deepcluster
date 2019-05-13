import argparse
import sys
import os 
from os.path import join as pjoin
import time
import random

import faiss
import numpy as np
from glob import glob
# from PIL import Image
import pandas as pd


from matplotlib.backends.qt_compat import QtGui, QtCore, QtWidgets

QPixmap = QtGui.QPixmap
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QFont = QtGui.QFont
QImage = QtGui.QImage 

QSize = QtCore.QSize
QSizeF= QtCore.QSizeF
QRect= QtCore.QRect
QRectF= QtCore.QRectF

QWidget = QtWidgets.QWidget
QGraphicsGridLayout  = QtWidgets.QGraphicsGridLayout
QGraphicsScene  = QtWidgets.QGraphicsScene
QGraphicsWidget  = QtWidgets.QGraphicsWidget
QGridLayout = QtWidgets.QGridLayout
QGraphicsPixmapItem= QtWidgets.QGraphicsPixmapItem

from PIL.ImageQt import ImageQt

from matplotlib.patches import Polygon
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.style.use('seaborn') 

from minmax import MinMax


######################################################################
parser = argparse.ArgumentParser(description='UI for large scale data-guided asset extraction')

parser.add_argument('--img_dir', help='The path to the actual dataset')
parser.add_argument('--csv', help='CSV containing the Properties of the dataset')
parser.add_argument('--fcsv', help='CSV containing the Features of the dataset')
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

    base = np.array([xlim[0], ylim[0]])
    width = np.array([xlim[1], 0])
    height = np.array([0, ylim[1]])

    quad_points = np.vstack([base, base+height, (base+height)+width, base+width])
    return quad_points

def pixmap_from_name(name):
        img = ImageQt(name)
        # print(type(img))
        w, h = img.width(), img.height()
        # print('image shape: {}x{}'.format(h, w))
        pixmap = QPixmap.fromImage(QImage(img))
        pixmap.detach()
        return pixmap

######################################################################

class ImagePane(QGraphicsWidget):
    clicked = QtCore.Signal(int)
    def __init__(self, parent=None, idx=None):
        super(ImagePane, self).__init__(parent=parent)
        self.idx = idx
        self.pixmap = QGraphicsPixmapItem(self)
        self.active_opacity = 1.0
        self.inactive_opacity = 0.8

        self._first_image_set = False
        self.size = 300

        self.pixmap.setOpacity(self.inactive_opacity)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        # print('Entered pane', self.rect())
        self.pixmap.setOpacity(self.active_opacity)
        self.update()
        
    def hoverLeaveEvent(self, event):
        # print('left pane', self.rect())
        self.pixmap.setOpacity(self.inactive_opacity)
        self.update()

    def set_image(self, image):
        self.pixmap.setPixmap(image.scaled(QSize(self.size, self.size)))
        self.pixmap.setOpacity(self.inactive_opacity)
        self.update()

    def sizeHint(self, which, constraint=QSizeF()):
        return  QSizeF(self.size, self.size) #self.pixmap.boundingRect().size()

    def boundingRect(self):
        return QRectF(0, 0,self.size,self.size)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.idx)

class ImageGrid(QGraphicsWidget):
    def __init__(self,
                parent=None,
                size=(4,4)):
        super(ImageGrid, self).__init__(parent=parent)

        self.num_panes = size[0]*size[1]
        self.nrows = size[0]
        self.ncols = size[1]

        layout = QGraphicsGridLayout()
        self.panes = {ii:ImagePane(self, idx=ii) for ii in range(self.num_panes)}

        for ii in range(self.num_panes):
            grid = self._linear2grid(ii)
            row = grid[0]
            col = grid[1]

            # print(self.panes[ii], row, col)
            layout.addItem(self.panes[ii], row, col)

        self.setLayout(layout)

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
            self.panes[idx].set_image(img)

        self.update()

class ImageViewer(QtWidgets.QGraphicsView):
    def __init__(self, 
                parent=None,
                size=(10,10)):
        super(ImageViewer, self).__init__()
        
        self.resize(800,800)
        self._scene = QGraphicsScene(self)
        self.image_grid = ImageGrid(size=size)

        self._scene.addItem(self.image_grid)
        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.ViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30))) #define dark gray background color
        self.setFrameShape(QtWidgets.QFrame.NoFrame)


    def resizeEvent(self, event):
        self.fit_in_view()
    
    def fit_in_view(self):
        rect = self.image_grid.rect()
        if not rect.isNull():
            # print(random.randint(1,1000), rect)
            self.setSceneRect(rect)

            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = max(viewrect.width() / scenerect.width(),
                            viewrect.height() / scenerect.height())
            self.scale(factor, factor)

    def set_image(self, idxes, images):
        self.image_grid.set_image(idxes, images)

class FilterDataFrame(object):
    def __init__(self,
                 df=None):
        super(FilterDataFrame, self).__init__()
        self.df = df
        self.numeric_cols = self.df.select_dtypes([np.number]).columns.values
        self.num_elem = self.df.shape[0]
        self.active_sets = {self.numeric_cols[i]:set(range(self.num_elem)) for i in range(len(self.numeric_cols))}
        self.min_vals = {self.numeric_cols[i]:np.min(df[self.numeric_cols[i]]) for i in range(len(self.numeric_cols))}
        self.max_vals = {self.numeric_cols[i]:np.max(df[self.numeric_cols[i]]) for i in range(len(self.numeric_cols))}

        self.total_active_set = set()
        self.update_active_set()

    def filter(self, attribute, min, max):
        assert attribute in self.numeric_cols
        satisfy_min = set(self.df.index[self.df.loc[:, attribute] > min])
        satisfy_max = set(self.df.index[self.df.loc[:, attribute] < max])
        self.active_sets[attribute] = satisfy_min & satisfy_max
        self.update_active_set()
        
    def update_active_set(self):
        self.total_active_set = self.active_sets[self.numeric_cols[0]]
        for s in self.active_sets.values():
            self.total_active_set = self.total_active_set & s
    def get_active_set(self):
        return self.total_active_set

class FacApp(QtWidgets.QMainWindow):
    def __init__(self, 
                args=None,
                parent=None):

        super(FacApp, self).__init__(parent)
        
        ## Layout and aesthetics
        self.ncols = 4
        self.nrows = 4
        self.n_subplots = self.ncols * self.nrows
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
        
        self.slider_to_attr = {self.text_resolution_h: 'height',
                               self.text_resolution_v: 'width',
                               self.text_num_floors: 'floors',
                               self.text_height: 'floors',
                               self.text_occlusion: 'total_occlusion',
                               self.text_blur: 'noblur',
                               self.text_viewing_angle: 'view_angle',
                               self.text_number_windows: 'num_windows',
                               self.text_aspect_ratio: 'aspect_ratio'}

        self.pane_to_idx = []

        #PANTONE 3553 C
        self.highlight_color = (0, 0.423, 0.690, 0.8)
        self.highlight_edge_color = (0, 0.423, 0.690, 1)

        if args.debug:
            print('Debug mode')
            self.image_list = None

        if args is not None:
            print('Loading Images...')
            self.img_dir = args.img_dir
            print('Loaded Properties...')
            self.prop_df = pd.read_csv(args.csv)
            self.filter = FilterDataFrame(self.prop_df)
            self.image_names = self.prop_df['name']
            self.num_images = len(self.image_names)
            print('Loaded Properties')

            print('Loading Features...')
            self.feat_df = pd.read_csv(args.fcsv, memory_map=True)
            print('Loaded Features')

            assert self.feat_df.shape[0] == self.prop_df.shape[0]

            print('property columns', self.prop_df.columns)
            print('Loaded {} images '.format(self.num_images))


        ######## Attach Model to the app #################

        ####### Set up the GUI ##################
        self.setWindowTitle('DeFeat GAX')
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QGridLayout(self.centralwidget)

        self.display_pane = QWidget(self.centralwidget)
        self.slider_pane = QWidget(self.centralwidget)
        self.hover_pane = QWidget(self.centralwidget)
        self.search_pane = QWidget(self.centralwidget)

        self.gridLayout.addWidget(self.slider_pane, 0, 3, 3, 1)
        self.gridLayout.addWidget(self.display_pane, 0, 0, 3, 3)
        self.gridLayout.addWidget(self.hover_pane, 3, 0, 1, 3)
        self.gridLayout.addWidget(self.search_pane, 3, 3, 1, 1)


        #####################################################################################
        self.display_pane_layout = QtWidgets.QVBoxLayout(self.display_pane)
        self.image_viewer = ImageViewer(size=(self.nrows,self.ncols))
        self.display_pane_layout.addWidget(self.image_viewer)

        
        for _, pane in self.image_viewer.image_grid.panes.items():
            pane.set_image(pixmap_from_name('/home/parawr/Projects/clusterFacadeData/superFacade/Austria/'
                            'Austria_Vienna_relation1684007_wall_1_0_ET967GUXryN8CB1BLEqmKQ_VP_0_0_FId_5638_.jpg'))

        self.connect_panes()

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

        # self.slider10 =  MinMax(self.slider_pane)
        # self.slider10.set_name(self.text_aspect_ratio)
        # self.slider_pane_layout.addWidget(self.slider10)

        self.slider_widget_to_attr = {'slider1': 'height',
                                      'slider2': 'width',
                                      'slider3': 'floors',
                                      'slider4': 'floors',
                                      'slider5': 'total_occlusion',
                                      'slider6': 'noblur',
                                      'slider7': 'view_angle',
                                      'slider8': 'num_windows',
                                      'slider9': 'aspect_ratio',}

        self.connect_sliders(9)

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
    
    def connect_panes(self):
        for _, pane in self.image_viewer.image_grid.panes.items():
            pane.clicked.connect(self.on_click)

    def connect_sliders(self, num_sliders):
        for ii in range(num_sliders):
            slider_string = 'slider' + str(ii+1)
            curr_slider = getattr(self, slider_string)

            _attr = self.slider_widget_to_attr[slider_string]
            _min = self.filter.min_vals[_attr]
            _max = self.filter.max_vals[_attr]

            curr_slider.set_limits(_min, _max)
            curr_slider.changed.connect(self.on_slider_change)


    def load_images(self):
        
        self.pane_to_idx = list(np.random.randint(0, self.num_images, self.n_subplots).ravel())

        # self.pane_to_idx = []        
        # for i, _ in enumerate(self.image_viewer.image_grid.panes.values()):
        #     self.pane_to_idx.append(self.idx[i])

        self.update_from_idx(list(range(self.n_subplots)))

    def update_from_idx(self, idxes):
        end = time.time()
        images = []

        for ii in idxes:
            name = pjoin(self.img_dir,self.image_names[self.pane_to_idx[ii]])
            images.append(pixmap_from_name(name))

        self.image_viewer.set_image(idxes, images)
        print('Time to update screen: {:.4f}'.format(time.time() - end))


    def search(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a file')
        # detect which switch is on

        # compute the features

        # perform the lookup in the appropriate space (facade/windows)

        # update the display
        #TODO
        pass

    def on_slider_change(self, name, _min, _max):
        # We have sets of individual indices filtered
        # end = time.time()
        # figure out which filter changed
        _attr = self.slider_to_attr[name]
        if not _attr in self.filter.numeric_cols:
            raise ValueError('Invalid Atribute to filter')
        # perform a lookup in the DataFrame
        self.filter.filter(_attr, _min, _max)
        # Find the new indices for the changed attribute
        active_set = self.filter.get_active_set()

        # Find curent indices that are no longer Valid, and replace

        invalid_idxes = list(set(self.pane_to_idx).difference(active_set))
        num_invalid = len(invalid_idxes)
        before = self.pane_to_idx

        if num_invalid == 0:
            return
        
        new_idxes = random.sample(active_set, num_invalid)

        panes = []
        for ii, invalid_idx in enumerate(invalid_idxes):
            pane = self.pane_to_idx.index(invalid_idx)
            self.pane_to_idx[pane] = new_idxes[ii]
            panes.append(pane)

        self.update_from_idx(panes)

        # print(time.time() - end)
        print(_attr, _min, _max, len(active_set))    
        
    def on_click(self, idx):
        im_idx = self.pane_to_idx[idx]
        print('Clicked on ', self.image_names[im_idx])

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
    # df = pd.read_csv(args.csv, memory_map=True)
    # aa = FilterDataFrame(df)
    # print(aa.numeric_cols)
    # print(len(aa.active_sets))
    # print(aa.min_vals)
    # print(aa.max_vals)
    # aa.filter('shop', 0.1, 1)
    # aa.filter('num_windows', 4, 15)
    # print(len(aa.total_active_set))
    # num_to_show = min(10, len(aa.total_active_set))
    # for ii in range(num_to_show):
    #     print(df.loc[list(aa.total_active_set)[ii], 'name'])

    # print(aa.df.loc[])
    main(args)
