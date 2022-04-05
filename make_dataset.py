import numpy as np
import cv2
import glob
import os
from util import load_image_into_numpy_array


def get_images_with_labels(p):
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

    paths = [
        r"c:\users\dek\Desktop\tardigrade movies\outpy",
        r"c:\users\dek\Desktop\tardigrade movies\outpy.1",
        r"c:\users\dek\Desktop\tardigrade movies\outpy.2",
        r"c:\users\dek\Desktop\tardigrade movies\outpy.3",
        r"c:\users\dek\Desktop\tardigrade movies\outpy.4",
        r"c:\users\dek\Desktop\tardigrade movies\outpy.5",
        r"c:\users\dek\Desktop\tardigrade movies\outpy.6",
        r"c:\users\dek\Desktop\tardigrade movies\test",
        # causes errors
        #r"c:\users\dek\Desktop\tardigrade movies\tracking"
        ]

    for path in paths:
        image_label_files.update(get_images_with_labels(path))


    return image_label_files