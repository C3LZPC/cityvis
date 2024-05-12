
import math
import os
import numpy as np
import requests
import zipfile

from io import BytesIO
from PIL import Image, ImageDraw
from osgeo import osr, gdal

# Based on https://stackoverflow.com/questions/14177744/how-does-perspective-transformation-work-in-pil
def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = np.matrix(matrix, dtype = np.float64)
    B = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)

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

def dl_tile_if_not_exists_OSM(x, y, z):
    file_name = f"cache/dltiles/{z},{x},{y}.png"
    try:
        f = open(file_name, "rb")
        f.close()
    except:
        print(f"Downloading: {file_name}")
        imgurl = f"http://tile.openstreetmap.org/{z}/{x}/{y}.png"
        imgstr = requests.get(imgurl, headers = {"User-Agent": "Python3 - one time DL"})
        tile = Image.open(BytesIO(imgstr.content))
        tile.save(file_name)

def dl_tile_if_not_exists_G(x, y, z):
    file_name = f"cache/dltiles/g_{z},{x},{y}.png"
    try:
        f = open(file_name, "rb")
        f.close()
    except:
        print(f"Downloading: {file_name}")
        headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
        layer = "s" # h = roads only ; m = standard roadmap ; p = terrain ; r = somehow altered roadmap ; s = satellite only ; t = terrain only ; y = hybrid
        imgurl = f"http://mt.google.com/vt/lyrs={layer}&x={x}&y={y}&z={z}"
        imgstr = requests.get(imgurl, headers = headers)
        tile = Image.open(BytesIO(imgstr.content))
        tile.save(file_name)

def dl_tile_if_not_exists(x, y, z, type = "OSM"):
    if type == "OSM":
        dl_tile_if_not_exists_OSM(x, y, z)
    if type == "G":
        dl_tile_if_not_exists_G(x, y, z)



##########



tile_size = 256
Z = 17

try:
    f = open("cache/AHN4_R_25EZ1.TIF", "rb")
    f.close()
except:
    url = "https://ns_hwh.fundaments.nl/hwh-ahn/ahn4/03a_DSM_0.5m/R_25EZ1.zip"
    urlstr = requests.get(url, headers = {"User-Agent": "Python3 - one time DL"})
    with open("cache/AHN4_R_25EZ1.zip", "wb") as f:
        f.write(urlstr.content)
    with zipfile.ZipFile("cache/AHN4_R_25EZ1.zip","r") as f:
        f.getinfo("R_25EZ1.TIF").filename = "cache/AHN4_R_25EZ1.TIF"
        f.extract("R_25EZ1.TIF")

try:
    f = open("cache/AHN3_R_25EZ1.TIF", "rb")
    f.close()
except:
    url = "https://ns_hwh.fundaments.nl/hwh-ahn/AHN3/DSM_50cm/R_25EZ1.zip"
    urlstr = requests.get(url, headers = {"User-Agent": "Python3 - one time DL"})
    with open("cache/AHN3_R_25EZ1.zip", "wb") as f:
        f.write(urlstr.content)
    with zipfile.ZipFile("cache/AHN3_R_25EZ1.zip","r") as f:
        f.getinfo("R_25EZ1.TIF").filename = "cache/AHN3_R_25EZ1.TIF"
        f.extract("R_25EZ1.TIF")

try:
    os.mkdir("cache/dltiles")
except:
    pass

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
gt = ds.GetGeoTransform() # gt = ( xoff, a, b, yoff, d, e ) # (120000.0, 0.5, 0.0, 493750.0, 0.0, -0.5)

outimg = Image.new("RGB", (width, height))

for x in range(width):
    print(f"{x} / {width} = {x / width * 100}%")
    for y in range(height):
        #print(x, y)

        xp = gt[0] + gt[1] * x + gt[2] * y
        yp = gt[3] + gt[4] * x + gt[5] * y
        #print(xp, yp)
        coords = transform.TransformPoint(xp, yp)
        #print(coords)
        xt, yt = deg2num2(coords[0], coords[1], Z, True)
        #print(xt, yt)
        ixt = int(xt)
        iyt = int(yt)

        # OSM
        #dl_tile_if_not_exists(ixt, iyt, Z)
        #tile = f"cache/dltiles/{Z},{ixt},{iyt}.png"

        # G
        dl_tile_if_not_exists(ixt, iyt, Z, "G")
        tile = f"cache/dltiles/g_{Z},{ixt},{iyt}.png"


        #print(tile)
        tile = Image.open(tile).convert("RGBA")
        px = tile.load()
        #print(tile.getpixel((int((xt - ixt) * tile_size), int((yt - iyt) * tile_size))))
        #print(px[int((xt - ixt) * tile_size), int((yt - iyt) * tile_size)])
        r, g, b, a = tile.getpixel((int((xt - ixt) * tile_size), int((yt - iyt) * tile_size)))
        draw = ImageDraw.Draw(outimg, "RGBA")
        draw.point((x, y), (r, g, b, a))

outimg.save(f"cache/exported.png")



