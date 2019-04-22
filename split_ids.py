import numpy as np
import sys
import os
from numpy.core.defchararray import add

class_id = sys.argv[1]

ratio1 = int(sys.argv[2])
ratio2 = int(sys.argv[3])
ratio3 = int(sys.argv[4])
assert(ratio1 + ratio2 + ratio3 == 100)

DIR = os.path.dirname(os.path.realpath(__file__))
ID_DIR = os.path.join(DIR, 'shapenetcore_ids')
DATASET_DIR = os.path.join(DIR, 'ShapeNetCore.v2/{}'.format(class_id))

if not os.path.exists(DATASET_DIR):
    print("please download the ShapeNetCore v.2 dataset, and place it into the same directory as this file")
    sys.exit(0)

if not os.path.exists(ID_DIR):
    os.mkdir( ID_DIR, 0777 );

obj_ids = np.array(next(os.walk(DATASET_DIR))[1])
obj_ids = add(class_id + '/', obj_ids)
np.random.shuffle(obj_ids)

a = int(float(ratio1) * 0.01 * len(obj_ids))
b = int(float(ratio1 + ratio2) * 0.01 * len(obj_ids))

train, validate, test = obj_ids[:a], obj_ids[a:b], obj_ids[b:]

print('Total: %d' % len(obj_ids))
print('Train: %d' % len(train))
print('Validate: %d' % len(validate))
print('Test: %d' % len(test))

np.savetxt(os.path.join(ID_DIR, '{}_trainids.txt'.format(class_id)), train, fmt='%s')
np.savetxt(os.path.join(ID_DIR, '{}_valids.txt'.format(class_id)), validate, fmt='%s')
np.savetxt(os.path.join(ID_DIR, '{}_testids.txt'.format(class_id)), test, fmt='%s')
