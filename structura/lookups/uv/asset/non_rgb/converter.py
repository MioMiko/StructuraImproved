from PIL import Image
from os import popen

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    Image.open(img_path).convert('RGBA').save(f'result/{img_path}')
