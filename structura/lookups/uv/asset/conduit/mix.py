from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    img = Image.open(img_path)
    target = Image.new('RGBA',(12,24))
    target.paste(img.crop((0,0,12,12)),(0,0),img.crop((0,0,12,12)))
    target.paste(img.crop((12,0,24,12)),(0,12),img.crop((12,0,24,12)))
    target.save(f'result/{img_path}')
