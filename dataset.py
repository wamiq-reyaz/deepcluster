import os
import pandas as pd
import numpy as np
import scipy.misc as m
from PIL import Image
from torch.utils import data
from torchvision import transforms

class facDataset(data.Dataset):

    def __init__(self, root=None, csv=None):

        self.root = root
        self.df = pd.read_csv(csv)
        # print(self.df.columns)
        self.names = self.df['name']

        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
        self.transform = transforms.Compose([transforms.Resize(256),
                        transforms.CenterCrop(224),
                        transforms.ToTensor(),
                        normalize])


    def __len__(self):
        return len(self.names)

    def __getitem__(self, index):
        img_path = os.path.join(self.root, self._get_parent(index), 'Extracted_facades', self.names[index])
        with Image.open(img_path) as _img:
            return self.transform(_img)
            #_img = Image.open(img_path).convert('RGB')


    def _get_parent(self, idx):
        name = self.names[idx]
        if 'Austria' in name:
            return 'Austria_Vienna'
        elif 'Belgium' in name:
            return 'Belgium_Brussels'
        elif 'China' in name:
            return 'China_HK'
        elif 'Denmark' in name:
            return 'Denmark_Copenhagen'
        elif 'France_Paris' in name:
            return 'France_Paris'
        elif 'Germany' in name:
            return 'Germany_Berlin'
        elif 'Greece' in name:
            return 'Greece_Athens'
        elif 'Italy' in name:
            return 'Italy_Rome'
        elif 'Netherlands' in name:
            return 'Netherlands_Amsterdam'
        elif 'Romania' in name:
            return 'Romania_Bucharest'
        elif 'Switzerlan' in name:
            return 'Switzerlan_Bern'
        elif 'UK_Lon' in name:
            return 'UK_London'
        elif 'USA_Chi' in name:
            return 'USA_Chicago'
        elif 'USA_Dallas' in name:
            return 'USA_Dallas'
        elif 'USA_Hawaii' in name:
            return 'USA_Hawaii'
        elif 'USA_Los' in name:
            return 'USA_LosAngeles'
        elif 'USA_New' in name:
            return 'USA_NewYork'
        else:
            raise ValueError("What the fuck have you done wrong")

if __name__ == '__main__':
    # TODO write tests
    pass
