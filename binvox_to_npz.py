import os
import sys
import traceback
import numpy as np
#from scipy import ndimage

DIR = os.path.dirname(os.path.realpath(__file__))
data_types = ['test', 'train', 'val']
ID_DIR = os.path.join(DIR, 'shapenetcore_ids')
BINVOX_FILE = os.path.join(DIR, 'ShapeNetCore.v2/{}/{}/models/model_normalized.solid.binvox')
OUTPUT_DIR = os.path.join(DIR, 'npz_files')

def read_as_3d_array(fp):
    '''With regards to https://github.com/dimatura/binvox-rw-py'''

    line = fp.readline().strip()
    if not line.startswith(b'#binvox'):
        raise IOError('Not a binvox file')

    dims = list(map(int, fp.readline().strip().split(b' ')[1:]))
    translate = list(map(float, fp.readline().strip().split(b' ')[1:]))
    scale = list(map(float, fp.readline().strip().split(b' ')[1:]))[0]
    dummyline = fp.readline()

    #print('Dims: {}'.format(dims))
    #print('Translate: {}'.format(translate))
    #print('Scale: {}'.format(scale))

    raw_data = np.frombuffer(fp.read(), dtype=np.uint8)

    values, counts = raw_data[::2], raw_data[1::2]
    data = np.repeat(values, counts).astype(np.bool)
    data = data.reshape(dims)

    return data

def center_image(data):
    orig_shape = data.shape

    # Remove all zero rows in all axes
    p0, p1, p2 = np.where(data != 0)
    small_arr = data[
        min(p0) : max(p0) + 1,
        min(p1) : max(p1) + 1,
        min(p2) : max(p2) + 1
    ]

    # https://stackoverflow.com/a/44874779
    # Create array of original shape and center image there.
    big_arr = np.zeros(data.shape, data.dtype)

    p = [0, 0, 0]
    for i in range(len(small_arr.shape)):
        p[i] = (big_arr.shape[i] - small_arr.shape[i]) // 2

    big_arr[
        p[0] : p[0] + small_arr.shape[0],
        p[1] : p[1] + small_arr.shape[1],
        p[2] : p[2] + small_arr.shape[2]
    ] = small_arr

    return big_arr

def downscale_image(data, input_scale, output_scale):
    ''' With regards to https://stackoverflow.com/a/4624923'''
    if input_scale == output_scale:
        return data

    data = data.reshape([
        output_scale, input_scale // output_scale,
        output_scale, input_scale // output_scale,
        output_scale, input_scale // output_scale,
    ]).mean(5).mean(3).mean(1)

    return np.array(data, dtype=bool)

def rotate_image(data):
    # Original axis order is xzy, change to yxz
    data = np.transpose(data, (2, 0, 1))
    #data = ndimage.rotate(data, 90, (1, 0))
    return data

def test():
    data = None
    with open('test.binvox', 'rb') as f:
        data = read_as_3d_array(f)
        print(data.shape)

    data = center_image(data)
    data = rotate_image(data)
    data = downscale_image(data, data.shape[0], 32)

    print(data.shape)
    print(float(np.count_nonzero(data)) / float(data.size))

    np.savez('test_vox_out.npz', data)

def run():
    class_id = sys.argv[1]

    for data_type in data_types:
        id_filepath = os.path.join(ID_DIR, '{}_{}ids.txt'.format(class_id, data_type))
        ids = open(id_filepath).readlines()
        ids = [i.strip().split('/')[-1] for i in ids if len(i.strip()) != 0]
        to_delete = []

        npz_filename = '{}_{}_voxels.npz'.format(class_id, data_type)
        npz_filepath = os.path.join(OUTPUT_DIR, npz_filename)

        print('Generating {}'.format(npz_filepath))
        arr_output = np.zeros((len(ids), 32, 32, 32))

        for i, obj_id in enumerate(ids):
            bv_filename = BINVOX_FILE.format(class_id, obj_id)
            arr = None

            try:
                with open(bv_filename, 'rb') as f:
                    arr = read_as_3d_array(f)
            except IOError:
                print('{} does not have a binvox file, removing from ID list'.format(obj_id))
                to_delete.append(i)
                continue

            arr = center_image(arr)
            arr = rotate_image(arr)
            arr = downscale_image(arr, 128, 32)

            arr_output[i, :, :, :] = arr

        np.savez(npz_filepath, arr_output)
        print('Created {}'.format(npz_filepath))

        if to_delete:
            with open(id_filepath, 'r+') as f:
                lines = f.readlines()
                f.seek(0)
                for i, l in enumerate(lines):
                    if not i in to_delete:
                        f.write(l)
                f.truncate()
            print('Removed {} samples from {} set'.format(len(to_delete), data_type))

if __name__ == '__main__':
    #test()
    run()
