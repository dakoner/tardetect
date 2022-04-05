import numpy as np
import cv2
import glob
import os
from util import load_image_into_numpy_array


def get_images_with_tardigrade_labels(p):
    g = glob.glob(os.path.join(p, "*.labels"))
    image_label_files = {}
    for i in g:
        l = open(i).readlines()
        if l != []:
            e = eval('\n'.join(l))
            gt_boxes = []
            if e != []:
                imf = i.removesuffix(".labels")
                im = cv2.imread(imf)
                if im is None:
                    continue
                for label in e:
                    y1, x1 = label[1]/im.shape[1], label[2]/im.shape[0]
                    y2, x2 = (label[1]+label[5])/im.shape[1], (label[2]+label[6])/im.shape[0]
                    gt_boxes.append(np.array([x1, y1, x2, y2], dtype=np.float32))
                image_label_files[imf] = np.array(gt_boxes)
    return image_label_files
  

def get_dataset():
        
    image_label_files = {}
    path = r"c:\users\dek\desktop\tardigrade movies\outpy"
    image_label_files.update(get_images_with_tardigrade_labels(path))

    path = r"c:\users\dek\desktop\tardetect\tardigrade movies\outpy.1"
    image_label_files.update(get_images_with_tardigrade_labels(path))

    return image_label_files