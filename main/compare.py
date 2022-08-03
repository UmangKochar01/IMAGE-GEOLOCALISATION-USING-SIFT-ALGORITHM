import cv2
import sys
import os.path
import numpy as np
import glob

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="myapp")


'''
def get_exif(filename):
    print('filenameeeeeeeeeeeeee',filename)
    exif = Image.open(filename)._getexif()

    if exif is not None:
        for key, value in exif.items():
            name = TAGS.get(key, key)
            exif[name] = exif.pop(key)

        if 'GPSInfo' in exif:
            for key in exif['GPSInfo'].keys():
                name = GPSTAGS.get(key,key)
                exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)

    return exif
'''

def get_exif(filename):
    exif = Image.open(filename)._getexif()

    if exif is None:
        return

    exif_data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)

        # GPS情報は個別に扱う．
        if tag == "GPSInfo":
            gps_data = {}
            for t in value:
                gps_tag = GPSTAGS.get(t, t)
                gps_data[gps_tag] = value[t]

            exif_data[tag] = gps_data
        else:
            exif_data[tag] = value

    return exif_data

def get_coordinates(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info[key] = ( str(e[0][0]/e[0][1]) + '°' +
                          str(e[1][0]/e[1][1]) + '′' +
                          str(e[2][0]/e[2][1]) + '″ ' +
                          ref )

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]

def get_decimal_coordinates(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info[key] = (e[0] + (e[1] / 60.0) + (e[2] / 3600.0)) * (-1 if ref in ['S','W'] else 1)

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]


def drawMatches(img1, kp1, img2, kp2, matches):

    #img1 = cv2.resize(img1,(100,100))
    #img2 = cv2.resize(img2,(100,100))

    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')
    out[:rows1,:cols1] = np.dstack([img1])
    out[:rows2,cols1:] = np.dstack([img2])
    for mat in matches:
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0, 1), 1)   
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0, 1), 1)
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0, 1), 1)
    return out

def compare(filename1, filename2):
    img1 = cv2.resize(cv2.imread(filename1),(100,100))          # queryImage
    img2 = cv2.resize(cv2.imread(filename2),(100,100))          # trainImage

    # Initiate SIFT detector
    sift = cv2.xfeatures2d.SIFT_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    #print(len(kp1))
    #print(len(kp2))

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.match(des1,des2)
    #print(len(matches))
    
    matches = sorted(matches, key=lambda val: val.distance)
    
    img3 = drawMatches(img1,kp1,img2,kp2,matches[:25])

    # Show the image
    #cv2.imshow('Matched Features', img3)
    #cv2.waitKey(0)
    #cv2.destroyWindow('Matched Features')
    return(kp1,kp2)


#img = input('Enter Image Name:')
def findLocation(img):

    diff = [0]*len(glob.glob("Dataset/*.jpg"))
    files = glob.glob("Dataset/*.jpg")
    for i,filename in enumerate(files):
    #for i in range(0,3):
        kp1,kp2 = compare(img,str(filename))
        print(len(kp1))
        print(len(kp2))
        diff[i] = abs(len(kp1)-len(kp2))
    print("diff ::",diff)

    res_index = diff.index(min(diff))
    ID = files[res_index]
    print("ID ::", ID)

    exif = get_exif(str(ID))
    print(exif['GPSInfo'])
    cordinates = get_decimal_coordinates(exif['GPSInfo'])

    print("cordinates ::",cordinates)

    location = geolocator.reverse(str(cordinates[0])+','+str(cordinates[1]))
    print(location.address)
    return(location.address)

