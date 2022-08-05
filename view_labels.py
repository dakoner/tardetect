import numpy as np
import cv2
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"    
import math
import tensorflow as tf
import random
# Fine-tune!
from model import build_model_and_restore_weights, prepare_data_for_training
from util import load_images
from classes import num_classes, category_index, tardigrade_class_id
from make_dataset import get_dataset
import shutil

BASE=r"z:\src"

# Visualize the rubber tardigrades as a sanity check
def visualize_tardigrades(filenames, train_images, gt_boxes, gt_classes, category_index, dummy_scores):
    fnames = open("fnames.txt", 'w')
    for idx in range(len(train_images)-1):
        s = train_images[idx]
        shape = np.array([s.shape[0], s.shape[1]])
        boxes = gt_boxes[idx]
        classes = gt_classes[idx]
        fname = filenames[idx]
        img = cv2.imread(fname)
        for i in range(len(classes)):
            print(boxes[i])
            box = np.array(boxes[i]*np.repeat(shape, repeats=2)).astype(np.int32)
            print(box)
            pt1 = (box[1], box[0])
            pt2 = (box[3], box[2])
            cv2.rectangle(img, pt1, pt2, (255,0,0), 2)
        ofname = fname + ".labelled"
        cv2.imwrite("tmp.png", img)
        shutil.copyfile("tmp.png", ofname)
        fnames.write(ofname + "\n")
    fnames.close()

image_label_files = get_dataset()
filenames = list(image_label_files.keys())

train_images = load_images(filenames)
# TODO: look up values using filenames keys
gt_boxes, gt_classes = zip(*[image_label_files[filename] for filename in filenames])
dummy_scores, gt_box_tensors, gt_classes_one_hot_tensors, train_image_tensors = prepare_data_for_training(train_images, gt_boxes, gt_classes, num_classes)
visualize_tardigrades(filenames, train_images, gt_boxes, gt_classes, category_index, dummy_scores)