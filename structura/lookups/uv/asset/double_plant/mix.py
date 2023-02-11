from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *_top.png').read().strip('\n').split('\n'):
    upper = Image.open(img_path)
    lower = Image.open(sub(r'(.*)_top.png',r'\1_bottom.png',img_path))
    target = Image.new('RGBA',(16,32),(255,255,255,0))
    target.paste(upper,(0,0),upper)
    target.paste(lower,(0,16),lower)
    target.save(sub(r"(.*?)_top.png",r'result/\1.png',img_path))
