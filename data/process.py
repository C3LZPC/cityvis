
import numpy as np
import gc
import json
import torch
import torch.nn.functional as F
import torchvision

from PIL import Image

def mem_fmt(num) -> str:
	postfix = "B"
	mem = 0.0
	if num / (1024 ** 1) > 1:
		postfix = "KB"
		mem = num / (1024 ** 1)
	if num / (1024 ** 2) > 1:
		postfix = "MB"
		mem = num / (1024 ** 2)
	if num / (1024 ** 3) > 1:
		postfix = "GB"
		mem = num / (1024 ** 3)
	if num / (1024 ** 4) > 1:
		postfix = "TB"
		mem = num / (1024 ** 4)

	return f"{mem:.4f} {postfix}"

def print_free_mem(torch_device) -> None:
	mem = torch.cuda.mem_get_info(device = torch_device)
	print(f"Free mem: {mem_fmt(mem[0])} / total mem: {mem_fmt(mem[1])} on {torch_device}\n")


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
transform = torchvision.transforms.Compose([torchvision.transforms.PILToTensor()])

meta_data = {
	"step_size": 512, # 513, 1025, 2049, 4097 : some game terrain handling algorithms require 2**n + 1 map sizes
	"min_height": 0.0,
	"max_height": 0.0,
	"x_step": 0.5,
	"y_step": 0.5,
	"x": 0,
	"y": 0
}


ahn3 = Image.open("cache/AHN3_R_25EZ1.TIF")
ahn3 = transform(ahn3).to(device)
print_free_mem(device)

ahn4 = Image.open("cache/AHN4_R_25EZ1.TIF")
ahn4 = transform(ahn4).to(device)
print_free_mem(device)

color = Image.open("cache/exported.png")
color = transform(color).to(device)
print_free_mem(device)

red = torch.gt(ahn3 - ahn4, 5.0)
color[0] = color[0].masked_fill(red, 0xff)
color[1] = color[1].masked_fill(red, 0x00)
color[2] = color[2].masked_fill(red, 0x00)
del red
gc.collect()
torch.cuda.empty_cache()
print_free_mem(device)


blue = torch.lt(ahn3 - ahn4, -5.0)
color[0] = color[0].masked_fill(blue, 0x00)
color[1] = color[1].masked_fill(blue, 0x00)
color[2] = color[2].masked_fill(blue, 0xff)
del blue
gc.collect()
torch.cuda.empty_cache()
print_free_mem(device)


max_map = torch.maximum(ahn3, ahn4)
print_free_mem(device)


meta_data["min_height"] = torch.min(torch.minimum(ahn3, ahn4)).to(torch.device("cpu")).item()
meta_data["max_height"] = torch.max(max_map).to(torch.device("cpu")).item()
while meta_data["max_height"] >= 1e+3: # The highest building on earth is ~830m  **NOTHING**  should be 3.4028234663852886e+38 tall
	max_map = torch.where(max_map < meta_data["max_height"], max_map, 0.0)
	meta_data["max_height"] = torch.max(max_map).to(torch.device("cpu")).item()

meta_data["x"] = int(max_map.shape[1] / meta_data['step_size']) + 1
meta_data["y"] = int(max_map.shape[2] / meta_data['step_size']) + 1

print(f"Min height: {meta_data['min_height']}")
print(f"Max height: {meta_data['max_height']}")
print(f"Major iterations X: {meta_data['x']} - map size X: {meta_data['x_step'] * max_map.shape[1]}")
print(f"Major iterations Y: {meta_data['y']} - map size Y: {meta_data['y_step'] * max_map.shape[2]}")

del ahn3
del ahn4
gc.collect()
torch.cuda.empty_cache()
print_free_mem(device)

# Quantize data and get it into the right device memory
print(max_map)
max_map = torch.add(max_map, abs(meta_data["min_height"]))
print(max_map)
#max_map = torch.where(max_map < 0.0, max_map, 0.0)
#print(max_map)
max_map = torch.quantize_per_tensor(max_map, meta_data["max_height"] / 256, 0, torch.quint8).int_repr().to(torch.device("cpu"))
print(max_map)
color = color.to(torch.device("cpu"))


# Iterate through the map by step_size
for x in range(int(max_map.shape[1] / meta_data['step_size']) + 1):
	for y in range(int(max_map.shape[2] / meta_data['step_size']) + 1):
		
		# Export color and height maps
		filename_height = f"{meta_data['step_size']}/{x}_{y}_height.png"
		filename_color = f"{meta_data['step_size']}/{x}_{y}_color.png"
		#print(f"{filename_height}, {filename_color}")

		m = max_map[:, x * meta_data['step_size']:(x + 1) * meta_data['step_size'] + 1, y * meta_data['step_size']:(y + 1) * meta_data['step_size'] + 1]
		c = color[:, x * meta_data['step_size']:(x + 1) * meta_data['step_size'] + 1, y * meta_data['step_size']:(y + 1) * meta_data['step_size'] + 1]
		pad_x = 513 - m.shape[1]
		pad_y = 513 - m.shape[2]

		if pad_x > 0:
			#print(f"m size: {m.shape}, padding_needed: {pad_x}, {pad_y}")
			m = F.pad(m, (0, 0, 0, pad_x), "replicate")
			#print(f"new_size: {m.shape}")
			#print(f"c size: {c.shape}, padding_needed: {pad_x}, {pad_y}")
			c = F.pad(c, (0, 0, 0, pad_x), "replicate")
			#print(f"new_size: {c.shape}")
		if pad_y > 0:
			#print(f"m size: {m.shape}, padding_needed: {pad_x}, {pad_y}")
			m = F.pad(m, (0, pad_y), "replicate")
			#print(f"new_size: {m.shape}")
			#print(f"c size: {c.shape}, padding_needed: {pad_x}, {pad_y}")
			c = F.pad(c, (0, pad_y), "replicate")
			#print(f"new_size: {c.shape}")

		torchvision.io.write_png(m, filename_height, 9)
		torchvision.io.write_png(c, filename_color, 9)

# Export metadata
try:
	with open(f"{meta_data['step_size']}/metadata.json", "w") as f:
		f.write(json.dumps(meta_data, indent = 2))
except Exception as e:
	with open(f"{meta_data['step_size']}/metadata.json", "x") as f:
		f.write(json.dumps(meta_data, indent = 2))

