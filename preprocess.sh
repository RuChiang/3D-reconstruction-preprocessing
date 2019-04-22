#!/bin/bash

class_id=$1
ratio_1=$2
ratio_2=$3
ratio_3=$4

python split_ids.py $class_id $ratio_1 $ratio_2 $ratio_3
sudo blender --background --python render.py $class_id
python binvox_to_npz.py $class_id
python png_to_npz.py $class_id
