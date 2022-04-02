
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

from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from classes import num_classes, category_index

from util import load_image_into_numpy_array, plot_detections
from model import build_model_and_restore_weights
BASE=r'z:\src'



# Run inference on the test set and assemble into a movie
def run_inference(detection_model):
    
  test_image_dir = os.path.join(BASE, r"tardetect\tardigrade movies\test")
  test_images_np = []

  for i in range(1, 50):#len(glob.glob(os.path.join(test_image_dir, 'out*.png')))):
    print(i)
    image_path = os.path.join(test_image_dir, 'out.%04d.png' % i)
    test_images_np.append(np.expand_dims(
        load_image_into_numpy_array(image_path), axis=0))

  # Again, uncomment this decorator if you want to run inference eagerly
  @tf.function
  def detect(input_tensor):
    """Run detection on an input image.

    Args:
      input_tensor: A [1, height, width, 3] Tensor of type tf.float32.
        Note that height and width can be anything since the image will be
        immediately resized according to the needs of the model within this
        function.

    Returns:
      A dict containing 3 Tensors (`detection_boxes`, `detection_classes`,
        and `detection_scores`).
    """
    preprocessed_image, shapes = detection_model.preprocess(input_tensor)
    prediction_dict = detection_model.predict(preprocessed_image, shapes)
    return detection_model.postprocess(prediction_dict, shapes)

  # Note that the first frame will trigger tracing of the tf.function, which will
  # take some time, after which inference should be fast.

  label_id_offset = 1
  for i in range(len(test_images_np)):
    input_tensor = tf.convert_to_tensor(test_images_np[i], dtype=tf.float32)
    detections = detect(input_tensor)

    plot_detections(
        test_images_np[i][0],
        detections['detection_boxes'][0].numpy(),
        detections['detection_classes'][0].numpy().astype(np.uint32)
        + label_id_offset,
        detections['detection_scores'][0].numpy(),
        category_index, figsize=(15, 20), image_name="gif_frame_" + ('%02d' % i) + ".jpg")

detection_model = build_model_and_restore_weights()

ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore("tardigrade-1-1")

run_inference(detection_model)
