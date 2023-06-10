from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    (
        Image.open(img_path)
        .crop((0,0,16,4))
        .rotate(90,expand=True)
        .save(f'result/{img_path.replace("side","arm")}')
    )
