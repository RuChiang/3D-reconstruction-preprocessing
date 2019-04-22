'''To use in Linux CLI:
1. Install Blender 2.79 (might work on older versions, does NOT work in 2.8)
2. Update global configs for your setup
3. Run "blender --background --python render.py <class id>"
'''

import math
import os
import random
import bpy
import sys


IMAGE_SIZE = 64
DISTANCE = 2.732
DIR = os.path.dirname(os.path.realpath(__file__))

ID_DIR = os.path.join(DIR, 'shapenetcore_ids')
OBJ_FILE = os.path.join(DIR, 'ShapeNetCore.v2/{}/{}/models/model_normalized.obj')
PNG_DIR = os.path.join(DIR, 'png_files/{}/{}')
blank_blend = os.path.join(DIR, 'blank.blend')

def set_camera_location(elevation, azimuth, distance):
    # set location
    x = 1 * math.cos(math.radians(-azimuth)) * math.cos(math.radians(elevation)) * distance
    y = 1 * math.sin(math.radians(-azimuth)) * math.cos(math.radians(elevation)) * distance
    z = 1 * math.sin(math.radians(elevation)) * distance
    camera = bpy.data.objects["Camera"]
    camera.location = x, y, z

    # look at center
    direction = - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

def render(directory, elevation=30, distance=DISTANCE):
    for azimuth in range(0, 360, 15):
        #filename = os.path.join(directory, 'e%03d_a%03d.png' % (elevation, azimuth))
        filename = os.path.join(directory, 'a%03d.png' % (azimuth))
        set_camera_location(elevation, azimuth, distance)
        bpy.context.scene.render.filepath = filename
        bpy.ops.render.render(write_still=True)

def setup():
    context = bpy.context
    context.scene.render.resolution_x = IMAGE_SIZE
    context.scene.render.resolution_y = IMAGE_SIZE
    context.scene.render.resolution_percentage = 100
    context.scene.render.use_antialiasing = True
    #context.scene.render.use_free_unused_nodes = True
    context.scene.render.use_free_image_textures = True
    context.scene.render.alpha_mode = 'TRANSPARENT'

    try:
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    except TypeError:
        print('RGBA not supported.')
        bpy.context.scene.render.image_settings.color_mode = 'RGB'

    # camera
    camera = bpy.data.cameras.values()[0]
    camera.sensor_width = 1
    camera.sensor_height = 1
    camera.lens = 1.8660254037844388

    # lighting
    light = bpy.data.objects['Lamp']
    light.data.energy = 1
    context.scene.world.light_settings.use_environment_light = True
    context.scene.world.light_settings.environment_energy = 0.5
    context.scene.world.light_settings.environment_color = 'PLAIN'

def load_obj(filename):
    bpy.ops.import_scene.obj(
        filepath=filename,
        use_smooth_groups=False,
        use_split_objects=False,
        use_split_groups=False,
    )
    object_id = len(bpy.data.objects) - 1
    obj = bpy.data.objects[object_id]
    bpy.context.scene.objects.active = obj

    # get max & min of vertices
    inf = 10000
    vertex_max = [-inf, -inf, -inf]
    vertex_min = [inf, inf, inf]
    for j in range(8):
        for i in range(3):
            vertex_max[i] = max(vertex_max[i], obj.bound_box[j][i])
            vertex_min[i] = min(vertex_min[i], obj.bound_box[j][i])
    dimensions = obj.dimensions  # = max - min

    # centering
    for i in range(3):
        obj.location[i] += (vertex_max[i] + vertex_min[i]) / 2

    # scaling
    scale = max(dimensions)
    for i in range(3):
        obj.scale[i] = obj.scale[i] / scale

    # materials
    for m in bpy.data.materials:
        m.ambient = 0.5
        m.use_shadeless = False
        m.use_transparency = False
        m.use_raytrace = False

def clear():
    bpy.ops.wm.open_mainfile(filepath=blank_blend)

def run():
    class_id = sys.argv[4]
    ids = []
    for dtype in ['train', 'test', 'val']:
        ids += open(os.path.join(ID_DIR, '{}_{}ids.txt'.format(class_id, dtype))).readlines()

    obj_ids = [i.strip().split('/')[-1] for i in ids if len(i.strip()) != 0]

    for i, obj_id in enumerate(obj_ids):
        this_png_dir = PNG_DIR.format(class_id, obj_id)
        if not os.path.exists(this_png_dir):
            os.makedirs(this_png_dir)

        clear()
        setup()
        load_obj(OBJ_FILE.format(class_id, obj_id))
        render(this_png_dir)

run()
