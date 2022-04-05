
import matplotlib
import matplotlib.pyplot as plt
import os
import random
import imageio
import glob
import numpy as np
from six import BytesIO
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf
import cv2
import time
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from classes import num_classes, category_index
import cv2
from util import load_image_into_numpy_array, plot_detections
from model import build_model_and_restore_weights
BASE=r'z:\src'


detection_model = build_model_and_restore_weights()

ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore("tardigrade-1-1")

label_id_offset = 1
  
fontScale = 1
color = (255, 0, 0)
thickness = 2
font = cv2.FONT_HERSHEY_SIMPLEX

#p = r"tardetect\tardigrade movies\outpy.2.mkv"
p = r"microscope_ui\outpy.mkv"

r = cv2.VideoCapture(os.path.join(BASE, p))

while True:
    ret, frame = r.read()
    if not ret: continue
    t0 = time.time()
    test_image_np = np.expand_dims(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), axis=0)
    input_tensor = tf.convert_to_tensor(test_image_np, dtype=tf.float32)
    preprocessed_image, shapes = detection_model.preprocess(input_tensor)
    prediction_dict = detection_model.predict(preprocessed_image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    scores = detections['detection_scores'][0].numpy()
    if scores[0] > .2:
        dbs = detections['detection_boxes'][0].numpy()
        db = dbs[0]
        s = frame.shape
        pt1 = int(db[1]*s[1]), int(db[0]*s[0])
        pt2 = int(db[3]*s[1]), int(db[2]*s[0])
        cv2.putText(frame, "%5.2f" % scores[0], pt2, font, fontScale, color, thickness, cv2.LINE_AA)
        cv2.rectangle(frame, pt1, pt2, (0, 128, 255), 1)
    cv2.imshow('im',frame)
    cv2.waitKey(1) 
    t1 = time.time()
    #print(t1-t0)