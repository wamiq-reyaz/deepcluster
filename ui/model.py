
import os
import time

from PIL import Image

import torch 
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torchvision import datasets, transforms

import models

class NNModel(object):
    def __init__(self,
                 arch='vgg16',
                 sobel=True,
                 weights=None,
                 transform=True):

        self.arch  = arch
        self.sobel = sobel
        self.weights = weights
        self.transform = transform
        self.model = models.__dict__[self.arch](sobel=self.sobel)

        self.load_weights()

        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
        self.transform = [transforms.Resize(256),
                            transforms.CenterCrop(224),
                            transforms.ToTensor(),
                            normalize]

    def load_weights(self):
        if os.path.isfile(self.weights):
            print('Model loading checkpoint {}'.format(self.weights))
            ckpt = torch.load(self.weights)
            self.model.load_state_dict(ckpt['state_dict'])
            print('Finished loading checkpoint')

        else:
            raise ValueError('Invalid checkpoint provided for the model')

    def compute_features(self, img):
        assert isinstance(img, Image)
        with torch.no_grad():
            input_tensor = self.transform(img).cuda()
            feat = self.model(input_tensor).data.cpu().numpy()

        return feat