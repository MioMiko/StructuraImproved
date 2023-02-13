from PIL import Image,ImageDraw
import numpy as np
from os import popen

layer = np.array(Image.new("RGBA",(16,16),(0,0,255,255)))
layer[1:15,1:15,3] = 0
layer = Image.fromarray(layer)

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    img = Image.open(img_path).convert("RGBA")
    img.paste(layer,(0,0),layer)
    img.save(f'result/{img_path}')
