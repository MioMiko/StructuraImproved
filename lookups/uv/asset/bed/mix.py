from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    target = Image.new('RGBA',(16,100))
    img = Image.open(img_path)
    tmp = img.crop((6,6,22,38)).rotate(180)
    target.paste(tmp,(0,0),tmp)
    tmp = img.crop((6,0,22,6)).rotate(180)
    target.paste(tmp,(0,32),tmp)
    tmp = img.crop((22,0,38,6)).rotate(180)
    target.paste(tmp,(0,38),tmp)
    tmp = img.crop((0,6,6,22)).rotate(90,expand = True)
    target.paste(tmp,(0,44),tmp)
    tmp = img.crop((0,22,6,38)).rotate(90,expand = True)
    target.paste(tmp,(0,50),tmp)
    tmp = img.crop((22,6,28,22)).rotate(-90,expand = True)
    target.paste(tmp,(0,56),tmp)
    tmp = img.crop((22,22,28,38)).rotate(-90,expand = True)
    target.paste(tmp,(0,62),tmp)
    tmp = img.crop((28,6,44,38))
    target.paste(tmp,(0,68),tmp)
    target.save(sub(r"(.*?).png",r'result/bed_\1.png',img_path))
