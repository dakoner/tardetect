import numpy as np
import cv2
import glob
import os
from util import load_image_into_numpy_array
from classes import name_to_id

BASE="/srv/media/Movies/Science/tardigrade movies/"
#BASE="x:/Science/tardigrade movies"

def get_images_with_labels(p):
    g = glob.glob(os.path.join(p, "*.labels"))
    image_label_files = {}
    for i in g:
        l = open(i).readlines()
        if l != []:
            e = eval('\n'.join(l))
            gt_boxes = []
            gt_classes = []
            if e != []:
                imf = i.removesuffix(".labels")
                im = cv2.imread(imf)
                if im is None:
                    continue
                for label in e:
                    y1, x1 = label[1]/im.shape[1], label[2]/im.shape[0]
                    y2, x2 = (label[1]+label[5])/im.shape[1], (label[2]+label[6])/im.shape[0]
                    gt_boxes.append(np.array([x1, y1, x2, y2], dtype=np.float32))
                    gt_classes.append(name_to_id[label[0]])
                image_label_files[imf] = np.array(gt_boxes), np.array(gt_classes)

    return image_label_files
  

def get_dataset():
        
    image_label_files = {}

    paths = [
        "outpy.1",
        "outpy.2",
        "outpy.3",
        "outpy.4",
        "outpy.5",
        "outpy.6",
        "outpy.7",
        "outpy.8",
        "outpy.9",
        "moult.eggs.1",
        "moult",
        "moult_egg",
        "test",
        "tracking"
        ]

    for path in paths:
        image_label_files.update(get_images_with_labels(os.path.join(BASE, path)))


    return image_label_files
