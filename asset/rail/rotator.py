from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    img = Image.open(img_path)
    target = Image.new('RGBA',(16,32))
    target.paste(img,(0,0),img)
    target.paste(img.rotate(90),(0,16),img.rotate(90))
    target.save(f'result/{img_path}')
