from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    Image.open(img_path).rotate(180).save(f'result/{img_path}')
