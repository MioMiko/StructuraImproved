from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 *_upper.png').read().strip('\n').split('\n'):
    upper = Image.open(img_path)
    lower = Image.open(sub(r'door_(.*)_upper.png',r'door_\1_lower.png',img_path))
    target = Image.new('RGBA',(16,64))
    target.paste(upper,(0,0),upper)
    target.paste(lower,(0,16),lower)
    target.paste(tmp := target.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,32),tmp)
    target.save(sub(r"(.*?)_(upper|lower).png",r'result/\1.png',img_path))
for img_path in popen(r'ls -1 *_top.png').read().strip('\n').split('\n'):
    upper = Image.open(img_path).convert("RGBA")
    lower = Image.open(sub(r'(.*)_top.png',r'\1_bottom.png',img_path)).convert("RGBA")
    target = Image.new('RGBA',(16,64))
    target.paste(upper,(0,0),upper)
    target.paste(lower,(0,16),lower)
    target.paste(tmp := target.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,32),tmp)
    target.save(sub(r"(.*?)_(top|bottom).png",r'result/\1.png',img_path))
