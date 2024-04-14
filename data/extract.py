

import matplotlib.pyplot as plt
import numpy as np
import math
import requests
from io import BytesIO
from PIL import Image

import os


# Based on https://stackoverflow.com/questions/28476117/easy-openstreetmap-tile-displaying-for-python


def degrees_to_decimal(degree : int, minutes : int, seconds : float):
    min_to_dec = float(minutes) / 60
    sec_to_dec = float(seconds) / 3600
    return degree + min_to_dec + sec_to_dec

def deg2num(lat_deg, lon_deg, zoom, as_float = False):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = (lon_deg + 180.0) / 360.0 * n
  ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
  if not as_float:
    xtile = int(xtile)
    ytile = int(ytile)
  return (xtile, ytile)
    
def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

def getImageCluster2(xmin, ymin, xmax, ymax, zoom):

    if xmax < xmin:
        a = xmax
        xmax = xmin
        xmin = a

    if ymax < ymin:
        a = ymax
        ymax = ymin
        ymin = a



    img_x = int((abs(xmax - xmin) + 1) * 256 - 1)
    img_y = int((abs(ymax - ymin) + 1) * 256 - 1)
    img_extents = (img_x, img_y)

    img = Image.new("RGB", img_extents)



    for xtile in range(int(xmin), int(xmax) + 1):
        for ytile in range(int(ymin), int(ymax) + 1):
            imgurl = f"http://tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"

            print("Opening: " + imgurl)
            imgstr = requests.get(imgurl, headers = {"User-Agent": "Python3 - one time DL"})

            try:
                tile = Image.open(BytesIO(imgstr.content))

                box_x = (xtile - xmin) * 256
                box_y = (ytile - ymin) * 255
                box_extents = (box_x, box_y)
                img.paste(tile, box = box_extents)

            except Exception as e:
                print("Couldn't download image:", e)
                tile = None
   
    return img

if __name__ == '__main__':
    #zoom = 13
    zoom = 17

    lat = degrees_to_decimal(52, 25, 53.21)
    lat_max = degrees_to_decimal(52, 22, 32.04)

    lon = degrees_to_decimal(4, 52, 22.59)
    lon_max = degrees_to_decimal(4, 56, 49.30)

    delta_lat = lat - lat_max
    delta_lon = lon - lon_max
    print(lat, lon, lat_max, lon_max)

    xmin, ymin = deg2num(lat, lon, zoom, True)
    xmax, ymax = deg2num(lat_max, lon_max, zoom, True)
    print(xmin, ymin, xmax, ymax)

    a = getImageCluster2(int(xmin), int(ymin), int(xmax),  int(ymax), zoom)

    # crop end
    x, y = a.size
    x = x - int(256 * (1 - (xmax - int(xmax))))
    y = y - int(256 * (1 - (ymax - int(ymax))))
    a = a.crop((0, 0, x, y))
    # crop beginning
    x, y = a.size
    c = int(256 * (xmin - int(xmin)))
    d = int(256 * (ymin - int(ymin)))
    a = a.crop((c, d, x, y))
    

    a.save(f"cache/{zoom},{xmin},{ymin}.png")

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.imshow(np.asarray(a))
    plt.show()
