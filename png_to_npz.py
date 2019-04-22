from PIL import Image
import numpy as np
import os
import sys

DIR = os.path.dirname(os.path.realpath(__file__))
data_types = ['test', 'train', 'val']
ID_DIR = os.path.join(DIR, 'shapenetcore_ids')
INPUT_DIR = os.path.join(DIR, 'png_files/{}/{}')
OUTPUT_DIR = os.path.join(DIR, 'npz_files')
class_id = sys.argv[1]

for data_type in data_types:
    ids = open(os.path.join(ID_DIR, '{}_{}ids.txt'.format(class_id, data_type))).readlines()
    ids = [i.strip().split('/')[-1] for i in ids if len(i.strip()) != 0]
    npz_filename = '{}_{}_images.npz'.format(class_id, data_type)
    npz_filepath = os.path.join(OUTPUT_DIR, npz_filename)
    print('Generating {}'.format(npz_filepath))
    arr_output = np.zeros((len(ids), 24, 4, 64, 64))

    for i, obj_id in enumerate(ids):
        obj_dir = INPUT_DIR.format(class_id, obj_id)
        angle_photos = [f for f in sorted(os.listdir(obj_dir))]

        for j, photo in enumerate(angle_photos):
            img = Image.open(os.path.join(obj_dir, photo))
            arr = np.array(img)
            arr = np.transpose(arr, (2, 0, 1))
            arr_output[i, j, :, :, :] = arr

    print(float(np.count_nonzero(arr_output)) / float(arr_output.size))
    np.savez(npz_filepath, arr_output)
    print('Created {}'.format(npz_filepath))


