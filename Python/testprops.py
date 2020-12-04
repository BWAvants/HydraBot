#!/usr/bin/python3

import cv2

cam = cv2.VideoCapture(0)

# camprops = []
# for prop in dir(cv2):
#     if prop.startswith('CAP_PROP_'):
#         camprops.append(prop)
#
# defaults = dict()
# for prop in camprops:
#     val = cam.get(getattr(cv2, prop))
#     if val != -1:
#         defaults[prop] = val
#
# for key, val in defaults.items():
#     print(key + ': ' + str(val))

# camprops = {'CAP_PROP_CONTRAST': 0.5,
#             'CAP_PROP_FORMAT': 16.0,
#             'CAP_PROP_SATURATION': 0.8203125,
#             'CAP_PROP_EXPOSURE': 0.0,
#             'CAP_PROP_BUFFERSIZE': 4.0,
#             'CAP_PROP_BACKEND': 200.0,
#             'CAP_PROP_TEMPERATURE': 4600.0,
#             'CAP_PROP_FRAME_HEIGHT': 480.0,
#             'CAP_PROP_GAIN': 0.0,
#             'CAP_PROP_GAMMA': 100.0,
#             'CAP_PROP_FRAME_WIDTH': 640.0,
#             'CAP_PROP_POS_MSEC': 0.0,
#             'CAP_PROP_BACKLIGHT': 1.0,
#             'CAP_PROP_FOURCC': 1448695129.0,
#             'CAP_PROP_FPS': 30.0,
#             'CAP_PROP_AUTO_EXPOSURE': 0.75,
#             'CAP_PROP_SHARPNESS': 3.0,
#             'CAP_PROP_BRIGHTNESS': 0.5,
#             'CAP_PROP_AUTO_WB': 1.0,
#             'CAP_PROP_HUE': 0.5,
#             'CAP_PROP_MODE': 1448695129.0,
#             'CAP_PROP_CONVERT_RGB': 1.0,
#             'CAP_PROP_WB_TEMPERATURE': 4600.0,
#             }

# camprops = {'CAP_PROP_CONTRAST': 0.5,
#             'CAP_PROP_SATURATION': 0.8203125,
#             'CAP_PROP_EXPOSURE': 0.0,
#             'CAP_PROP_FRAME_HEIGHT': 480.0,
#             'CAP_PROP_GAIN': 0.0,
#             'CAP_PROP_GAMMA': 100.0,
#             'CAP_PROP_FRAME_WIDTH': 640.0,
#             'CAP_PROP_BACKLIGHT': 1.0,
#             'CAP_PROP_FPS': 30.0,
#             'CAP_PROP_AUTO_EXPOSURE': 0.75,
#             'CAP_PROP_SHARPNESS': 3.0,
#             'CAP_PROP_BRIGHTNESS': 0.5,
#             'CAP_PROP_AUTO_WB': 1.0,
#             'CAP_PROP_HUE': 0.5,
#             'CAP_PROP_CONVERT_RGB': 1.0,
#             }
#

camprops = {
    'CAP_PROP_AUTOFOCUS': 1.0,
    'CAP_PROP_AUTO_EXPOSURE': 1.0,
    'CAP_PROP_BACKLIGHT': 0.0,
    'CAP_PROP_BRIGHTNESS': 8.0,
    'CAP_PROP_CONTRAST': 8.0,
    'CAP_PROP_CONVERT_RGB': 1.0,
    'CAP_PROP_EXPOSURE': -4.0,
    'CAP_PROP_FOCUS': 16.0,
    'CAP_PROP_FOURCC': 842094158.0,
    'CAP_PROP_FPS': 30.0,
    'CAP_PROP_FRAME_HEIGHT': 480.0,
    'CAP_PROP_FRAME_WIDTH': 640.0,
    'CAP_PROP_GAIN': 0.0,
    'CAP_PROP_GAMMA': 7.0,
    'CAP_PROP_HUE': 0.0,
    'CAP_PROP_MODE': 0.0,
    'CAP_PROP_POS_FRAMES': 0.0,
    'CAP_PROP_POS_MSEC': 0.0,
    'CAP_PROP_SAR_DEN': 1.0,
    'CAP_PROP_SAR_NUM': 1.0,
    'CAP_PROP_SATURATION': 7.0,
    'CAP_PROP_SHARPNESS': 6.0,
    'CAP_PROP_TEMPERATURE': 2800.0
}

for prop in camprops.keys():
    propnum = getattr(cv2, prop)
    default = cam.get(propnum)
    cam.set(propnum, -10000)
    minval = cam.get(propnum)
    cam.set(propnum, 10000)
    maxval = cam.get(propnum)
    camprops[prop] = (propnum, minval, default, maxval)

for key, val in camprops.items():
    print(key + ': ' + str(val))

"""
'CAP_PROP_BUFFERSIZE': 38, 1.0, 4.0, 10.0
"""