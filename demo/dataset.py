import os
import pandas as pd
import numpy as np
import scipy.misc as m
from PIL import Image
from torch.utils import data
from torchvision import transforms, Compose

class facDataset(data.Dataset):

    def __init__(self, root=None, csv=None):

        self.root = root
        self.df = pd.read_csv(csv)
        self.names = self.df['names']

        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
        self.transform = Compose([transforms.Resize(256),
                        transforms.CenterCrop(224),
                        transforms.ToTensor(),
                        normalize])


    def __len__(self):
        return len(self.names)

    def __getitem__(self, index):

        img_path = os.path.join(self.root, self.names[index])
        
        _img = Image.open(img_path).convert('RGB')

        sample = {'image': _img, 'label': 1}

        return self.transform(sample)


if __name__ == '__main__':
    # TODO write tests
    pass