import math
import matplotlib
import matplotlib.pyplot as plt
import glob
import cv2
import numpy as np
from PIL import Image
from object_detection.utils import visualization_utils as viz_utils
from six import BytesIO
import tensorflow as tf

def load_image_into_numpy_array(path):
  """Load an image from file into a numpy array.

  Puts image into numpy array to feed into tensorflow graph.
  Note that by convention we put it into a numpy array with shape
  (height, width, channels), where channels=3 for RGB.

  Args:
    path: a file path.

  Returns:
    uint8 numpy array with shape (img_height, img_width, 3)
  """
  img_data = tf.io.gfile.GFile(path, 'rb').read()
  image = Image.open(BytesIO(img_data))
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


def load_images(image_files):
    train_images_np = []
    for image_file in image_files:
        train_images_np.append(load_image_into_numpy_array(image_file))
    return np.array(train_images_np)

def plot_detections(image_np,
                    boxes,
                    classes,
                    scores,
                    category_index,
                    figsize=(12, 16),
                    image_name=None):
  """Wrapper function to visualize detections.

  Args:
    image_np: uint8 numpy array with shape (img_height, img_width, 3)
    boxes: a numpy array of shape [N, 4]
    classes: a numpy array of shape [N]. Note that class indices are 1-based,
      and match the keys in the label map.
    scores: a numpy array of shape [N] or None.  If scores=None, then
      this function assumes that the boxes to be plotted are groundtruth
      boxes and plot all boxes as black with no classes or scores.
    category_index: a dict containing category dictionaries (each holding
      category index `id` and category name `name`) keyed by category indices.
    figsize: size for the figure.
    image_name: a name for the image file.
  """
  image_np_with_annotations = image_np.copy()
  viz_utils.visualize_boxes_and_labels_on_image_array(
      image_np_with_annotations,
      boxes,
      classes,
      scores,
      category_index,
      use_normalized_coordinates=True,
      min_score_thresh=0.8)
  if image_name:
    plt.imsave(image_name, image_np_with_annotations)
  else:
    matplotlib.use('qtagg')
    plt.imshow(image_np_with_annotations)

# Visualize the rubber tardigrades as a sanity check
def visualize_tardigrades(train_images_np, gt_boxes, gt_classes, category_index, dummy_scores):
  matplotlib.use('qtagg')
  plt.figure(figsize=(30, 15))
  for idx in range(len(train_images_np)-1):
    n = math.ceil(math.sqrt(len(train_images_np)))    
    plt.subplot(n, n, idx+1)
    plot_detections(
        train_images_np[idx],
        gt_boxes[idx],
        np.array(gt_classes[idx], dtype=np.int32),
        dummy_scores, category_index)
  plt.show()
