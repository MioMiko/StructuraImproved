from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 door_*_upper.png').read().strip('\n').split('\n'):
    upper = Image.open(img_path)
    lower = Image.open(sub(r'door_(.*)_upper.png',r'door_\1_lower.png',img_path))
    target = Image.new('RGBA',(16,64))
    target.paste(upper,(0,0),upper)
    target.paste(lower,(0,16),lower)
    target.paste(tmp := target.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,32),tmp)
    target.save(sub(r"door_(.*?)_(upper|lower).png",r'result/door_\1.png',img_path))
