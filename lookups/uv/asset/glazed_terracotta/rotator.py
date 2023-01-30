from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    img = Image.open(img_path)
    target = Image.new('RGBA',(16,64))
    for i in range(4):
        target.paste(img,(0,16*i))
        img = img.rotate(-90)
    target.save(f'result/{img_path}')
