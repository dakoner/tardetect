

# By convention, our non-background classes start counting at 1.  Given
# that we will be predicting just one class, we will therefore assign it a
# `class id` of 1.
tardigrade_class_id = 1
num_classes = 1
category_index = {tardigrade_class_id: {'id': tardigrade_class_id, 'name': 'tardigrade'}}