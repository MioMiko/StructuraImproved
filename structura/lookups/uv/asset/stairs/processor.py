from PIL import Image,ImageDraw
import numpy as np
from os import popen

layer = np.array(Image.new("RGBA",(16,32),(0,0,255,0)))
layer[2:4,2:-2,3] = 255
layer[-4:-2,2:-2,3] = 255
layer = Image.fromarray(layer)

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    target = Image.new("RGBA",(16,32))
    img = Image.open(img_path)
    target.paste(img,(0,0),img)
    target.paste(img,(0,16),img)
    target.paste(layer,(0,0),layer)
    target.save(f'result/{img_path}')
