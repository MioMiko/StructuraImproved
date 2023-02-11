from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 glass_*.png | grep -P "glass_.*?_alpha.png"').read().strip('\n').split('\n'):
    bg = Image.new('RGB',(16,16),(255,255,255))
    img = Image.open(img_path)
    bg.paste(img,(0,0),img)
    bg.save(sub(r"glass_(.*?)_alpha.png",r'glass_\1.png',img_path))
