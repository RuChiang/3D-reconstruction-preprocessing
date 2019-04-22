# 3D reconstruction Preprocessing

This repository contains the preprocessing code of the [3D reconstruction](https://github.com/hiroharu-kato/mesh_reconstruction) in the paper [Neural 3D Mesh Renderer](http://hiroharu-kato.com/projects_en/neural_renderer.html) (CVPR 2018) by Hiroharu Kato, Yoshitaka Ushiku, and Tatsuya Harada.

As the input data provided by the author only contains the preprocessed input(in npz format), our team has constructed a pipeline that facilitate the preprocessing of the data from the ShapeNetCore dataset.

Using the pipeline, this repository also contains the preprocess npz files for the following classes

__"03636649" : "lamps"__ <br/>
__"03797390" : "mug"__ <br/>
__"02876657" : "bottle"__ <br/>

## Prerequisite
- Blender v2.79
- PIL
- bpy
- ShapeNetCore .v2 (Place it in this repo root)

## Run

To run data preprocessing, select an object class id from ShapeNetCore:

> ./preprocess.sh {class_id} {train_ratio} {validation_ratio} {test_ratio}

Note that 3 ratios should sum up to __100__

The preprocessed npz files for training can be found in npz_files directory.
Remember to move them to the [3D reconstruction](https://github.com/hiroharu-kato/mesh_reconstruction) project directory for further training and testing

> mv npz_files/\*.npz ~/mesh_reconstruction/data/dataset

## What happens when this script runs

Essentially it does all the data preprocessing for training the model, the processes include

- generating png files by taking photos of objects that belong to the specified class_id
- converting the png files to npz format
- converting the binvox files in the ShapeNetCore dataset of the objects into npz format

## Running the train/test code

For running the train and test code, move to the mesh

>cd ~/mesh_reconstruction <br/>
python mesh_reconstruction/train.py -eid singleclass_{class ID} -cls {class ID} -ls 0.001 -li 1000 -ni {number of iterations, 30-200k} <br/>
python mesh_reconstruction/test.py -eid singleclass_{class ID}

## Special Thanks
The team would like to thank the author __Hiroharu__ for providing us with the raw script for taking photos of the objects using Blender, and his detailed responses over the course of this project!!
