
from io import BytesIO
from PIL import Image

outimg = Image.new("RGB", (10000, 12500))


tile_size = 256
size_multiplier_x = 1.45
size_multiplier_y = 1.465

start_x = 67310 # 67309
end_x = 67335 # 67336 # 67337
x_offset = 18

start_y = 43039 # 43038
end_y = 43071 # 43072
y_offset = 105


for x in range(start_x, end_x + 1):
    for y in range(start_y, end_y + 1):
        tile = Image.open(f"cache/dltiles/17,{x},{y}.png")
        tile = tile.resize((int(tile_size * size_multiplier_x), int(tile_size * size_multiplier_y)), resample = Image.Resampling.NEAREST)
        outimg.paste(tile, box = ((x - start_x) * int(tile_size * size_multiplier_x) - x_offset, (y - start_y) * int(tile_size * size_multiplier_y) - y_offset))

outimg.save(f"cache/exported.png")



