import argparse
import sys
import os 
from os.path import join as pjoin
import time
import random


import faiss
import models
import numpy as np
from glob import glob
import pandas as pd

import torch 
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torchvision import transforms
from torchvision.transforms import Compose
import json

from matplotlib.backends.qt_compat import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

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

from PIL import Image
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
parser.add_argument('--pca', help='npz containing the pca of the dataset')
parser.add_argument('--mean', help='npz containing the mean of the dataset')
parser.add_argument('--win', action='store_true', default=False,
                    help='Turn on the window mode (default: False)')


parser.add_argument('--csv_win', help='CSV containing the Properties of the windows')
parser.add_argument('--fcsv_win', help='CSV containing the Features of the windows')
parser.add_argument('--pca_win', help='npz containing the pca of the dataset')
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

def _is_img_file(name):
        valid_ext = ['.png', '.jpeg', '.jpg', '.bmp', '.tiff']
        _ext = os.path.splitext(name)[1]

        if _ext in valid_ext:
            return True
        else:
            return False
######################################################################

class ImagePane(QGraphicsWidget):
    clicked = QtCore.Signal(int)
    def __init__(self, parent=None, idx=None):
        super(ImagePane, self).__init__(parent=parent)
        self.idx = idx
        self.img = None
        self.pixmap = QGraphicsPixmapItem(self)
        self.active_opacity = 1.0
        self.inactive_opacity = 0.8

        self._first_image_set = False
        self.size = 300
        self.imsize = self.size - 5

        self.is_orig_aspect = False

        self.pixmap.setOpacity(self.inactive_opacity)
        self.setAcceptHoverEvents(True)

    def show_original_aspect(self, temporary=False):
        if not temporary:
            self.is_orig_aspect = True
        img = self.img.scaled(QSize(self.imsize, self.imsize), 1)
        h, w = img.height(), img.width()
        left, top  = self._getTranslate(h, w)
        self.pixmap.setOffset(left, top)
        self.pixmap.setPixmap(img)
        self.update()

    def show_scaled_aspect(self):
        self.is_orig_aspect = False
        self.pixmap.setOffset(0, 0)
        self.pixmap.setPixmap(self.img.scaled(QSize(self.imsize, self.imsize), 0))
        self.update()


    def hoverEnterEvent(self, event):
        self.show_original_aspect(temporary=True)        
        self.pixmap.setOpacity(self.active_opacity)
        self.update()
        
    def hoverLeaveEvent(self, event):
        if not self.is_orig_aspect:
            self.show_scaled_aspect()
        self.pixmap.setOpacity(self.inactive_opacity)
        self.update()

    def set_image(self, image):
        self.img = image
        if self.is_orig_aspect:
            self.show_original_aspect()
        else:
            self.show_scaled_aspect()

    def sizeHint(self, which, constraint=QSizeF()):
        return   QSizeF(self.imsize, self.imsize) # self.pixmap.boundingRect().size()#

    def boundingRect(self):
        return QRectF(0, 0,self.size,self.size)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.idx)

    def _getTranslate(self, h, w):
        total_horiz = self.imsize - w
        right = total_horiz // 2

        total_vert = self.imsize - h
        top = total_vert // 2

        return right, top


class ImageGrid(QGraphicsWidget):
    def __init__(self,
                parent=None,
                size=(4,4)):
        super(ImageGrid, self).__init__(parent=parent)

        self.num_panes = size[0]*size[1]
        self.nrows = size[0]
        self.ncols = size[1]
        print('From image_grid, ', self.nrows, self.ncols)

        layout = QGraphicsGridLayout()
        self.panes = {ii:ImagePane(self, idx=ii) for ii in range(self.num_panes)}

        for ii in range(self.num_panes):
            row, col = self._linear2grid(ii)

            print(ii, row, col)
            layout.addItem(self.panes[ii], row, col)

        self.setLayout(layout)

    def _linear2grid(self, idx):
        row = idx // self.ncols
        col = idx % self.ncols

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
        # self.setFrameShape(QtWidgets.QFrame.NoFrame)


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

class QFileDialogPreview(QtWidgets.QFileDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(QFileDialogPreview, self).__init__(parent=parent, *args, **kwargs)
        self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)

        box = QtWidgets.QVBoxLayout()
        self.setFixedSize(self.width() + 250, self.height())

        self.mpPreview = QtWidgets.QLabel(self)
        self.mpPreview.setFixedSize(600, 600)
        self.mpPreview.setAlignment(QtCore.Qt.AlignCenter)
        self.mpPreview.setObjectName("labelPreview")
        box.addWidget(self.mpPreview)

        box.addStretch()

        print(self.layout())
        self.layout().addLayout(box, 3, 3, 1, 1)

        self.directoryEntered.connect(self.dir)
        self.currentChanged.connect(self.onChange)
        self.fileSelected.connect(self.onFileSelected)
        self.filesSelected.connect(self.onFilesSelected)

        self._fileSelected = None
        self._filesSelected = None

    def dir(self, dir):
        print('asfaf')

    def onChange(self, path):
        print('asfafd')
        pixmap = QtWidgets.QPixmap(path)
        if(pixmap.isNull()):
            self.mpPreview.setText("Preview")
        else:
            self.mpPreview.setPixmap(pixmap.scaled(self.mpPreview.width(), self.mpPreview.height()))

    def onFileSelected(self, file):
        print(file)
        self._fileSelected = file

    def onFilesSelected(self, files):
        print(files)
        self._filesSelected = files

    def getFileSelected(self):
        print(self._fileSelected)
        return self._fileSelected

    def getFilesSelected(self):
        return self._filesSelected

class kNN(object):
    def __init__(self,
                 feat=None,
                 dim=4096):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(feat)

    def nearest(self, feat, num=300):
        # print('Features', feat)
        # assert feat.squeeze().shape == (self.dim,)
        feat = np.ascontiguousarray(feat.reshape(1, -1).astype(np.float32))
        # print(self.index.d, feat.shape)
        return self.index.search(feat, num)

class FeatureExtractor(object):
    def __init__(self,
                arch='vgg16',
                weights=None,
                gpus=[0]):
        self.arch = arch
        self.gpus = gpus
        self.weights = weights

        self.model = models.__dict__[arch](sobel=True)
        self.model.top_layer = None
        self.model.features = torch.nn.DataParallel(self.model.features)
        self.model = self.model.cuda()
        cudnn.benchmark = True

        self._load_weights()

        self.model.top_layer = None
        self.model.classifier = nn.Sequential(*list(self.model.classifier.children())[:-1])

        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

        self.transform = Compose([transforms.Resize(256),
                                transforms.CenterCrop(224),
                                transforms.ToTensor(),
                                normalize])
        self.embedding = np.load('balanced_200_normalize_old_feat.npz')['arr_0']
        self.clusters = 


    def extract(self,
                img=None):
        _img_tensor = self.transform(img).cuda().unsqueeze(dim=0)
        self.model.eval()
        with torch.no_grad():
            _feat = self.model(_img_tensor).data.cpu().numpy()
        return _feat

    def _load_weights(self):
        if os.path.isfile(self.weights):
            print("=> loading checkpoint '{}'".format(self.weights))
            checkpoint = torch.load(self.weights)
            self.model.load_state_dict(checkpoint['state_dict'])
            print("=> loaded checkpoint")
        else:
            print("=> no checkpoint found at '{}'".format(self.weights))

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
        self.text_num_floors = 'Number of Floors'
        self.text_height = 'Height'
        self.text_occlusion = 'Occlusion'
        self.text_blur = 'Sharpness'
        self.text_viewing_angle = 'Viewing Angle'
        self.text_number_windows = 'Number of Windows'
        self.text_aspect_ratio = 'Aspect Ratio'

        self.searches = dict()
        
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
            # print('Loaded Properties...')
            self.prop_df = pd.read_csv(args.csv)
            self.filter = FilterDataFrame(self.prop_df)
            self.active_set = self.filter.get_active_set()

            self.image_names = self.prop_df['name']
            self.num_images = len(self.image_names)
            print('Loaded Properties')

            print('Loading Features...')
            self.feat_df = pd.read_csv(args.fcsv)
            if 'Unnamed: 0' in self.feat_df.columns:
                del self.feat_df['Unnamed: 0']
            if 'name' in self.feat_df.columns:
                del self.feat_df['name']
            print('Feature shape', self.feat_df.shape)

            self.pca = np.load(args.pca)['arr_0']
            self.mean = np.load(args.mean)['arr_0']

            print('Loaded Features')
            self.feat_dim = self.feat_df.shape[1]
            assert self.feat_df.shape[0] == self.prop_df.shape[0]

            print('Property Columns', self.prop_df.columns)
            print('Loaded {} images '.format(self.num_images))

            ######## Attach Model to the app #################

            print('Setting up CNN and search...')
            feat = self.feat_df.values.astype(np.float32)
            feat_contig = np.ascontiguousarray(self.feat_df.values.astype(np.float32))
            self.fac_knn = kNN(feat_contig, dim=self.feat_dim)

            print('Search set up')
            self.fac_extractor = FeatureExtractor(weights=args.weights)
            print('CNN set up')

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
        # self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        # self.canvas = FigureCanvas(self.figure)
        # self.canvas.setContentsMargins(0,0,0,0)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        # self.toolbar = NavigationToolbar(self.canvas, self)


        # self.hover_pane_layout.addWidget(self.canvas)

        if args.win:
            self.slider_widget_to_attr = {'slider1': 'height',
                                        'slider2': 'width',
                                        'slider3': 'aspect_ratio',
                                        'slider4': 'noblur',
                                        'slider5': 'view_angle',
                                        'slider6': 'normalized_x',
                                        'slider7': 'normalized_y',}

            self.slider_widget_to_text = {'slider1': 'Height',
                                        'slider2': 'Width',
                                        'slider3': 'Aspect Ratio',
                                        'slider4': 'Sharpness',
                                        'slider5': 'View Angle',
                                        'slider6': 'Normalized X',
                                        'slider7': 'Normalized Y',}

        else:
            self.slider_widget_to_attr = {'slider1': 'height',
                                          'slider2': 'width',
                                          'slider3': 'floors',
                                          'slider4': 'floors',
                                          'slider5': 'total_occlusion',
                                          'slider6': 'noblur',
                                          'slider7': 'view_angle',
                                          'slider8': 'num_windows',
                                          'slider9': 'aspect_ratio',}

            self.slider_widget_to_text = {'slider1': 'Resolution H',
                                        'slider2': 'Resolution V',
                                        'slider3': 'Floors',
                                        'slider4': 'Height',
                                        'slider5': 'Total Occlusion',
                                        'slider6': 'Sharpness',
                                        'slider7': 'View Angle',
                                        'slider8': 'Windows',
                                        'slider9': 'Aspect Ratio'}

        ## The home for all the sliders
        self.slider_pane_layout = QtWidgets.QVBoxLayout(self.slider_pane)
        self.slider1 =  MinMax(self.slider_pane)
        # self.slider1.set_name(self.text_resolution_h)
        # self.slider_pane_layout.addWidget(self.slider1)

        self.slider2 =  MinMax(self.slider_pane)
        # self.slider2.set_name(self.text_resolution_v)
        # self.slider_pane_layout.addWidget(self.slider2)
# 
        self.slider3 =  MinMax(self.slider_pane)
        # self.slider3.set_name(self.text_num_floors)
        # self.slider_pane_layout.addWidget(self.slider3)

        self.slider4 =  MinMax(self.slider_pane)
        # self.slider4.set_name(self.text_height)
        # self.slider_pane_layout.addWidget(self.slider4)

        self.slider5 =  MinMax(self.slider_pane)
        # self.slider5.set_name(self.text_occlusion)
        # self.slider_pane_layout.addWidget(self.slider5)

        self.slider6 =  MinMax(self.slider_pane)
        # self.slider6.set_name(self.text_blur)
        # self.slider_pane_layout.addWidget(self.slider6)

        self.slider7 =  MinMax(self.slider_pane)
        # self.slider7.set_name(self.text_viewing_angle)
        # self.slider_pane_layout.addWidget(self.slider7)

        if not args.win:
            self.slider8 =  MinMax(self.slider_pane)
            # self.slider8.set_name(self.text_number_windows)
            # self.slider_pane_layout.addWidget(self.slider8)

            self.slider9 =  MinMax(self.slider_pane)
        # self.slider9.set_name(self.text_aspect_ratio)
        # self.slider_pane_layout.addWidget(self.slider9)

        # self.slider10 =  MinMax(self.slider_pane)
        # self.slider10.set_name(self.text_aspect_ratio)
        # self.slider_pane_layout.addWidget(self.slider10)

    
        for ii in range(len(self.slider_widget_to_attr)):
            slider_string = 'slider' + str(ii+1)
            curr_slider = getattr(self, slider_string)
            curr_slider.set_name(self.slider_widget_to_text[slider_string])
            curr_slider.set_index(slider_string)
            self.slider_pane_layout.addWidget(curr_slider)

        self.connect_sliders(len(self.slider_widget_to_attr))

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
        self.toolButton_load_image.setText('Resample')
        self.toolButton_load_image.clicked.connect(self.load_images)

        self.search_pane_layout.addWidget(self.horiz_widget)
        self.search_pane_layout.addWidget(self.toolButton_search_image)
        self.search_pane_layout.addWidget(self.toolButton_load_image)

        elements_to_magnify = ['radioButton_facade', 'radioButton_window',
                               'radioButton_city', 'toolButton_load_image',
                               'toolButton_search_image']
        self.magnify_font(elements_to_magnify)
        # self.plot()

        # self.keyboardGrabber.connect(self.handle_keyboard)

    def keyPressEvent(self, event):
        print(event.key())
        key = event.key()
        if key == 65: #A
            for ii, pane in self.image_viewer.image_grid.panes.items():
                pane.show_original_aspect()
        elif key == 70: #F
            for ii, pane in self.image_viewer.image_grid.panes.items():
                pane.show_scaled_aspect()
        elif key == 78: # N
            self.load_images()
        elif key == 66:
            self.resize(2413, 2100)
            #
            pass
            # print('Saving JSON')
            # with open('ucl_facade_search.json' , 'w') as fd:
            #     json.dump(self.searches, fd, indent=4)

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
            print(_attr)
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
        d = QFileDialogPreview(self)
        file = d.getOpenFileName(self, 'Choose a file')

        # file = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a file')

        # if file.
        # detect which switch is on
        _is_active = None
        for ii, _attr in enumerate([ 'radioButton_facade','radioButton_window']):
            button = getattr(self, _attr)
            if button.isChecked():
                active_button = ii
                _is_active = True
                break

        fname = file[0]
        if not _is_active or not _is_img_file(fname):
            return

        # compute the features
        try:
            _img = Image.open(fname)
        except:
            print('Failed to open Image {}'.format(fname))
            return

        feat = self.fac_extractor.extract(_img)
        feat = np.ascontiguousarray(feat.astype(np.float32))
        
        feat = self.pca @ (feat - self.mean).reshape(-1, 1) # matrix multiplication
        print(file, active_button)
        print(self.feat_df.shape)

        # perform the lookup in the appropriate space (facade/windows)

        d, idxes = self.fac_knn.nearest(feat)
        idxes = list(idxes.ravel())

        bname = os.path.basename(fname)
        self.searches[bname] = [self.image_names[ii] for ii in idxes[:100]]

        # update the display
        valid_idx = set(idxes).intersection(self.active_set)

        counter = 0
        print(d.shape)
        for ii, idx in enumerate(idxes):
            if counter >= self.n_subplots:
                break
            if idx in valid_idx:
                self.pane_to_idx[counter] = idx
                print(d[0, ii])
                counter += 1
        # for ii, idx in enumerate(valid_idx):
        #     if ii >= self.n_subplots:
        #         break
        #     self.pane_to_idx[ii] = idx

        self.update_from_idx(list(range(self.n_subplots)))
        return

    def on_slider_change(self, name, _min, _max):
        # We have sets of individual indices filtered
        # end = time.time()
        # figure out which filter changed
        _attr = self.slider_widget_to_attr[name]
        if not _attr in self.filter.numeric_cols:
            raise ValueError('Invalid Atribute to filter')
        # perform a lookup in the DataFrame
        self.filter.filter(_attr, _min, _max)
        self.active_set = self.filter.get_active_set()

        # Find the new indices for the changed attribute
        # Find curent indices that are no longer Valid, and replace

        invalid_idxes = list(set(self.pane_to_idx).difference(self.active_set))
        num_invalid = len(invalid_idxes)
        before = self.pane_to_idx

        if num_invalid == 0:
            print(_attr, _min, _max, len(self.active_set))  
            return
        
        new_idxes = random.sample(self.active_set, num_invalid)

        panes = []
        for ii, invalid_idx in enumerate(invalid_idxes):
            pane = self.pane_to_idx.index(invalid_idx)
            self.pane_to_idx[pane] = new_idxes[ii]
            panes.append(pane)

        self.update_from_idx(panes)

        # print(time.time() - end)
        print(_attr, _min, _max, len(self.active_set))    
        
    def on_click(self, idx):
        im_idx = self.pane_to_idx[idx]
        print('Clicked on ', self.image_names[im_idx], im_idx)

    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = np.random.rand(400, 2)#[random.random() for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)
        self.figure.tight_layout()

        # discards the old graph
        ax.clear()

        # plot data
        ax.scatter(data[:, 0], data[:, 1])

        # refresh canvas
        self.canvas.draw()

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
