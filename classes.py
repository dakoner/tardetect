

# By convention, our non-background classes start counting at 1.  Given
# that we will be predicting just one class, we will therefore assign it a
# `class id` of 1.
tardigrade_class_id = 1
algae_class_id = 2
egg_class_id = 3
moult_class_id = 4
vorticella_class_id = 5
animacule_class_id = 6
junk_class_id = 7

num_classes = 1
category_index = {
        tardigrade_class_id: {'id': tardigrade_class_id, 'name': 'tardigrade'}
}


name_to_id = {
    'tardigrade': 1,
    'algae': 2,
    'egg': 3,
    'moult': 4,
    'vorticella': 5,
    'animacule': 6,
    'junk': 7
}