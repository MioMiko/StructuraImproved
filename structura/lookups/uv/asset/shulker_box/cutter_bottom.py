from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 shulker_*.png | grep -P "shulker_(?!(top)|(bottom)|(side)).*?.png"').read().strip('\n').split('\n'):
    img = Image.open(img_path).crop((32,28,48,44)).save(sub(r"shulker_(.*?).png",r'shulker_bottom_\1.png',img_path))
