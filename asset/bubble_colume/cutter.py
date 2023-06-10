from PIL import Image
from os import popen

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    Image.open(img_path).resize((16,512)).crop((0,0,16,16)).save(f'result/{img_path}')
