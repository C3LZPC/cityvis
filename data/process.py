
import numpy as np
import torch
import torchvision.transforms as transforms
import gc

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
    print(f"Free mem: {mem_fmt(mem[0])} / totoal mem: {mem_fmt(mem[1])} on {torch_device}\n")


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
transform = transforms.Compose([transforms.PILToTensor()])

meta_data = {
    "min_height": 0.0,
    "max_height": 0.0,
    "x_step": 0.5,
    "y_step": 0.5,
}


ahn3 = Image.open("AHN3_R_25EZ1.TIF")
ahn3 = transform(ahn3).to(device)
print_free_mem(device)

ahn4 = Image.open("AHN4_R_25EZ1.TIF")
ahn4 = transform(ahn4).to(device)
print_free_mem(device)


color = torch.zeros(3, ahn3.shape[1], ahn3.shape[2], device = device, dtype = torch.uint8)
print_free_mem(device)


red = torch.gt(ahn3, ahn4)
color[0].masked_fill(red, 0xff)
color[1].masked_fill(red, 0x00)
color[2].masked_fill(red, 0x00)
del red
gc.collect()
torch.cuda.empty_cache()
print_free_mem(device)


blue = torch.lt(ahn3, ahn4)
color[0].masked_fill(blue, 0x00)
color[1].masked_fill(blue, 0x00)
color[2].masked_fill(blue, 0xff)
del blue
gc.collect()
torch.cuda.empty_cache()
print_free_mem(device)


is_close = torch.isclose(ahn3, ahn4, rtol = 0, atol = 1e-1, equal_nan = True) # Ignore 10 cm of measurement error
color[0].masked_fill(is_close, 0x77)
color[1].masked_fill(is_close, 0x77)
color[2].masked_fill(is_close, 0x77)
del is_close
gc.collect()
torch.cuda.empty_cache()
print_free_mem(device)




max_map = torch.maximum(ahn3, ahn4).to(device)
print_free_mem(device)


meta_data["min_height"] = torch.min(torch.minimum(ahn3, ahn4)).to(torch.device("cpu")).item()
meta_data["max_height"] = torch.max(max_map).to(torch.device("cpu")).item()

print(f"Min height: {meta_data['min_height']}")
print(f"Max height: {meta_data['max_height']}")
print(f"Major iterations X: {max_map.shape[0] % 513 + 1} - map size X: {meta_data['x_step'] * max_map.shape[1]}")
print(f"Major iterations Y: {max_map.shape[1] % 513 + 1} - map size Y: {meta_data['y_step'] * max_map.shape[2]}")
print_free_mem(device)



'''
for i in range(ahn3.shape[0] % 513 + 1):
    for j in range(ahn3.shape[1] % 513 + 1):
        chunk = np.zeros((513, 513), np.int32)
        color = np.zeros((513, 513, 3), np.int8)
        for x in range(513):
            for y in range(513):
                if i * 513 + x >= ahn3.shape[0]:
                    chunk[x][y] = 0
                chunk[x][y]
                color[x][y]
        print(f"{(i, j)}...")

print(f"Export done")
'''

