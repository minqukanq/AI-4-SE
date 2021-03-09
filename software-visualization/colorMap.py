from matplotlib import cm
from PIL import Image
import numpy as np
import cv2
import os
import binascii

def get_FileSize(filePath):
    # filePath = unicode(filePath,'utf8')
    fsize = os.path.getsize(filePath)
    size = fsize/float(1024)
    return round(size,2)

def get_new_color_img(filename):
    size = get_FileSize(filename)
    n =   1
    if (size == 0):
        return 0
    if size < 10:
        width = int(32 * n)
    elif size < 30:
        width = int(64 * n)
    elif size < 60:
        width = int(128 * n)
    elif size < 100:
        width = int(256 * n)
    elif size < 200:
        width = int(384 * n)
    elif size < 500:
        width = int(512 * n)
    elif size < 1000:
        width = int(768 * n)
    else:
        width = int(1024 * n)

    with open(filename, 'rb') as f:
        content = f.read()
    hexst = binascii.hexlify(content)
    fh = np.array([int(hexst[i:i + 2], 16) for i in range(0, len(hexst), 2)])

    end = len(fh) - len(fh) % 3

    # b = fh[0:end:3]
    # g = fh[1:end:3]
    # r = fh[2:end:3]

    # r = fh[0:end:3]
    # b = fh[1:end:3]
    # g = fh[2:end:3]

    # r = fh[0:end:3]
    # g = fh[1:end:3]
    # b = fh[2:end:3]
    #
    # b = fh[0:end:3]
    # r = fh[1:end:3]
    # g = fh[2:end:3]
    #
    # g = fh[0:end:3]
    # b = fh[1:end:3]
    # r = fh[2:end:3]
    #
    g = fh[0:end:3]
    r = fh[1:end:3]
    b = fh[2:end:3]


    img2 = cv2.merge([b, g, r])
    img1 = img2[:len(b) - len(b) % width]
    img = np.reshape(img1, (width, len(b) // width, 3))

    return img

def get_jet():
    colormap_int = np.zeros((256, 3), np.uint8)
    colormap_float = np.zeros((256, 3), np.float)

    for i in range(0, 256, 1):
        colormap_float[i, 0] = cm.jet(i)[0]
        colormap_float[i, 1] = cm.jet(i)[1]
        colormap_float[i, 2] = cm.jet(i)[2]

        colormap_int[i, 0] = np.int_(np.round(cm.jet(i)[0] * 255.0))
        colormap_int[i, 1] = np.int_(np.round(cm.jet(i)[1] * 255.0))
        colormap_int[i, 2] = np.int_(np.round(cm.jet(i)[2] * 255.0))

    np.savetxt("../temp/jet_float.txt", colormap_float, fmt="%f", delimiter=' ', newline='\n')
    np.savetxt("../temp/jet_int.txt", colormap_int, fmt="%d", delimiter=' ', newline='\n')

def gray2color(gray_array, color_map):
    rows, cols = gray_array.shape
    color_array = np.zeros((rows, cols, 3), np.uint8)

    for i in range(0, rows):
        for j in range(0, cols):
            color_array[i, j] = color_map[gray_array[i, j]]

    return color_array


def test_gray2color(path):
    # gray_image = Image.open(path).convert("L")
    gray_image = path.convert("L")

    gray_array = np.array(gray_image)

    jet_map = np.loadtxt('/home/zhb/Documents/kk/Xlearn-master/pytorch/tool/jet_int.txt', dtype=np.int)
    color_jet = gray2color(gray_array, jet_map)
    return color_jet