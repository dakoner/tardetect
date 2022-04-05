
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

def prepare_data_for_training(train_images_np, gt_boxes, num_classes):
  # Convert class labels to one-hot; convert everything to tensors.
  # The `label_id_offset` here shifts all classes by a certain number of indices;
  # we do this here so that the model receives one-hot labels where non-background
  # classes start counting at the zeroth index.  This is ordinarily just handled
  # automatically in our training binaries, but we need to reproduce it here.

  label_id_offset = 1
  train_image_tensors = []
  gt_classes_one_hot_tensors = []
  gt_box_tensors = []

  for (train_image_np, gt_box_np) in zip(
      train_images_np, gt_boxes):
    train_image_tensors.append(tf.expand_dims(tf.convert_to_tensor(
        train_image_np, dtype=tf.float32), axis=0))
    gt_box_tensors.append(tf.convert_to_tensor(gt_box_np, dtype=tf.float32))
    zero_indexed_groundtruth_classes = tf.convert_to_tensor(
        np.ones(shape=[gt_box_np.shape[0]], dtype=np.int32) - label_id_offset)
    gt_classes_one_hot_tensors.append(tf.one_hot(
        zero_indexed_groundtruth_classes, num_classes))
  print('Done prepping data.')
  dummy_scores = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float32)  # give boxes a score of 100%
  return dummy_scores, gt_box_tensors, gt_classes_one_hot_tensors, train_image_tensors



BASE=r'z:\src'
#wget http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz
#tar -xf ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.tar.gz
#mv ssd_resnet50_v1_fpn_640x640_coco17_tpu-8/checkpoint models/research/object_detection/test_data/

# build model and restore weights for fine tuning
def build_model_and_restore_weights(num_classes):
  tf.keras.backend.clear_session()

  print('Building model and restoring weights for fine-tuning...', flush=True)
  pipeline_config = os.path.join(BASE,'tensorflow/models/research/object_detection/configs/tf2/ssd_resnet50_v1_fpn_640x640_coco17_tpu-8.config')
  checkpoint_path = os.path.join("ssd_resnet50_v1_fpn_640x640_coco17_tpu-8/checkpoint", 'ckpt-0')

  # Load pipeline config and build a detection model.
  #
  # Since we are working off of a COCO architecture which predicts 90
  # class slots by default, we override the `num_classes` field here to be just
  # one (for our new tardigrade-related classes).
  configs = config_util.get_configs_from_pipeline_file(pipeline_config)
  model_config = configs['model']
  model_config.ssd.num_classes = num_classes
  model_config.ssd.freeze_batchnorm = True
  detection_model = model_builder.build(
        model_config=model_config, is_training=True)

  # Set up object-based checkpoint restore --- RetinaNet has two prediction
  # `heads` --- one for classification, the other for box regression.  We will
  # restore the box regression head but initialize the classification head
  # from scratch (we show the omission below by commenting out the line that
  # we would add if we wanted to restore both heads)
  fake_box_predictor = tf.compat.v2.train.Checkpoint(
      _base_tower_layers_for_heads=detection_model._box_predictor._base_tower_layers_for_heads,
      # _prediction_heads=detection_model._box_predictor._prediction_heads,
      #    (i.e., the classification head that we *will not* restore)
      _box_prediction_head=detection_model._box_predictor._box_prediction_head,
      )
  fake_model = tf.compat.v2.train.Checkpoint(
            _feature_extractor=detection_model._feature_extractor,
            _box_predictor=fake_box_predictor)
  ckpt = tf.compat.v2.train.Checkpoint(model=fake_model)
  ckpt.restore(checkpoint_path).expect_partial()

  # Run model through a dummy image so that variables are created
  image, shapes = detection_model.preprocess(tf.zeros([1, 640, 640, 3]))
  prediction_dict = detection_model.predict(image, shapes)
  _ = detection_model.postprocess(prediction_dict, shapes)
  print('Weights restored!')

  return detection_model
