import numpy
import os,shutil
import binascii
from random import *
import colorMap
import cv2
import time

rs = Random()

save_path = '../data/img/'
color_path = 'grb_img/'

def getMatrixfrom_bin(filename, width = 512, oneRow = False):
    with open(filename, 'rb') as f:
        content = f.read()
    hexst = binascii.hexlify(content)
    fh = numpy.array([int(hexst[i:i+2],16) for i in range(0, len(hexst), 2)])
    if oneRow is False:
        rn = len(fh)/width
        fh = numpy.reshape(fh[:rn*width],(-1,width))
    fh = numpy.uint8(fh)
    return fh

def getMatrixfrom_asm(filename, startindex = 0, pixnum = 89478485):
    with open(filename, 'rb') as f:
        f.seek(startindex, 0)
        content = f.read(pixnum)
    hexst = binascii.hexlify(content)
    fh = numpy.array([int(hexst[i:i+2],16) for i in range(0, len(hexst), 2)])
    fh = numpy.uint8(fh)
    return fh

def get_FileSize(filePath):
    # filePath = unicode(filePath,'utf8')
    fsize = os.path.getsize(filePath)
    size = fsize/float(1024)
    return round(size,2)

if __name__ == '__main__':
    for txtfile in os.listdir('../data//txt'):
        if txtfile == '.DS_Store':
            continue
        if txtfile == '._ant-1.7.txt':
            continue
        if txtfile == '._.DS_Store':
            continue
        if txtfile == '._jEdit-4.0.txt':
            continue

        path_project = save_path + color_path + txtfile.split('.txt')[0]

        if not os.path.exists(path_project):
            os.makedirs(path_project)

        if not os.path.exists(path_project + '/buggy/'):
            os.makedirs(path_project + '/buggy/')

        if not os.path.exists(path_project + '/clean/'):
            os.makedirs(path_project + '/clean/')

        filename = '../data/txt/'+txtfile
        f = open(filename)
        class_num = 0
        java_num = 0
        no_num = 0
        for line in f:

            f_path = '../data/archives/'+line[:-3]
            label = line[-2:-1]
            start = time.process_time()
            if os.path.exists(f_path+'.class'):
                class_num = class_num + 1
                size = get_FileSize(f_path+'.class')
                if size == 0:
                    break
                im = colorMap.get_new_color_img(f_path+'.class')
                if label == '1':
                    path_save = path_project +'/buggy/'+''.join(line[:-3]).replace('/','_')+'.png'
                    cv2.imwrite(path_save, im)
                    # im.save(path_save)
                else:
                    path_save = path_project +'/clean/'+''.join(line[:-3]).replace('/','_')+'.png'
                    cv2.imwrite(path_save, im)
                    # im.save(path_save)
            elif os.path.exists(f_path+'.java'):
                java_num = java_num + 1
                size = get_FileSize(f_path + '.java')
                if size == 0:
                    break
                im = colorMap.get_new_color_img(f_path+'.java')
                if label == '1':
                    path_save = path_project + '/buggy/' + ''.join(
                        line[:-3]).replace('/', '_') + '.png'
                    cv2.imwrite(path_save, im)
                    # im.save(path_save)
                else:
                    path_save = path_project  + '/clean/' + ''.join(
                        line[:-3]).replace('/', '_') + '.png'
                    cv2.imwrite(path_save, im)
                    # im.save(path_save)
            else:
                no_num = no_num + 1
            end = time.process_time()
            image_time = str(end-start)

        print(class_num)
        print(java_num)
        print(no_num)
