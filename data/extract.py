

import matplotlib.pyplot as plt
import math
import numpy as np
import os
import requests

from io import BytesIO
from PIL import Image
from osgeo import osr, gdal



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

def deg2num2(lat_deg, lon_deg, zoom, as_float = False):
    # based on https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    lat_rad = math.radians(lat_deg)
    n = 2 ** zoom
    tile_x = n * ((lon_deg + 180) / 360)
    tile_y = n * (1 - (math.asinh(math.tan(lat_rad)) / math.pi)) / 2
    if not as_float:
        tile_x = int(tile_x)
        tile_y = int(tile_y)
    return (tile_x, tile_y)


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



    img_x = int((abs(xmax - xmin) + 1) * 256)
    img_y = int((abs(ymax - ymin) + 1) * 256)
    #img_x = int((abs(xmax - xmin) + 1) * 256 - 1)
    #img_y = int((abs(ymax - ymin) + 1) * 256 - 1)
    img_extents = (img_x, img_y)

    img = Image.new("RGB", img_extents)



    for xtile in range(int(xmin), int(xmax) + 1):
        for ytile in range(int(ymin), int(ymax) + 1):
            imgurl = f"http://tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"

            #headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
            #layer = "s" # h = roads only ; m = standard roadmap ; p = terrain ; r = somehow altered roadmap ; s = satellite only ; t = terrain only ; y = hybrid
            #imgurl = f"http://mt.google.com/vt/lyrs={layer}&x={xtile}&y={ytile}&z={zoom}"

            print("Opening: " + imgurl)
            imgstr = requests.get(imgurl, headers = {"User-Agent": "Python3 - one time DL"})
            #imgstr = requests.get(imgurl, headers = headers)

            try:
                tile = Image.open(BytesIO(imgstr.content))
                tile.save(f"cache/dltiles/{zoom},{xtile},{ytile}.png")

                box_x = (xtile - xmin) * 256
                box_y = (ytile - ymin) * 256
                #box_y = (ytile - ymin) * 255
                box_extents = (box_x, box_y)
                img.paste(tile, box = box_extents)

            except Exception as e:
                print("Couldn't download image:", e)
                tile = None
   
    return img

if __name__ == "__main__":
    #zoom = 13
    zoom = 17
    
    ds = gdal.Open("cache/AHN4_R_25EZ1.TIF")
    old_cs = osr.SpatialReference()
    old_cs.ImportFromWkt(ds.GetProjectionRef())
    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563, AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0, AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328, AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]
    """
    new_cs = osr.SpatialReference()
    new_cs.ImportFromWkt(wgs84_wkt)
    transform = osr.CoordinateTransformation(old_cs, new_cs)

    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()

    lat = gt[0]
    lat_max = gt[0] + width * gt[1] + height * gt[2]
    
    lon = gt[3] + width * gt[4] + height * gt[5]
    lon_max = gt[3]


    min_latlong = transform.TransformPoint(lat, lon)
    max_latlong = transform.TransformPoint(lat_max, lon_max)
    print(f"Points: {min_latlong} - {max_latlong}")

    xmin, ymin = deg2num2(min_latlong[0], min_latlong[1], zoom, True)
    xmax, ymax = deg2num2(max_latlong[0], max_latlong[1], zoom, True)
    xmin -= 1
    xmax -= 1
    ymin -= 1
    ymax -= 1
    print(f"Coords: ({xmin}, {ymin}) - ({xmax}, {ymax})")

    a = getImageCluster2(int(xmin), int(ymin), int(xmax),  int(ymax), zoom)


    """
    # crop end
    x, y = a.size
    x = x - round(256 * (1 - (xmax - int(xmax))))
    y = y - round(256 * (1 - (ymax - int(ymax))))
    a = a.crop((0, 0, x, y))
    
    # crop beginning
    x, y = a.size
    c = round(256 * (xmin - int(xmin)))
    d = round(256 * (ymin - int(ymin)))
    a = a.crop((c, d, x, y))
    """

    """
    #crop end
    x, y = a.size
    x = x - round(256 * (1 - (xmin - int(xmin))))
    y = y - round(256 * (1 - (ymin - int(ymin))))
    a = a.crop((0, 0, x, y))

    # crop beginning
    x, y = a.size
    c = round(256 * (xmax - int(xmax)))
    d = round(256 * (ymax - int(ymax)))
    a = a.crop((c, d, x, y))
    """

    """
    a = a.resize((10000, 12500), resample = Image.Resampling.NEAREST)
    a.save(f"cache/{zoom},({int(xmin)},{int(ymin)}) - ({int(xmax)},{int(ymax)}).png")
    """
