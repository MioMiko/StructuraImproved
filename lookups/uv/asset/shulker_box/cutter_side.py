from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 shulker_*.png | grep -P "shulker_(?!(top)|(bottom)|(side)).*?.png"').read().strip('\n').split('\n'):
    target = Image.new('RGB',(16,16))
    img = Image.open(img_path)
    target.paste(img.crop((0,16,16,28)),(0,0))
    target.paste(img.crop((0,44,16,52)),(0,8),img.crop((0,44,16,52)))
    target.save(sub(r"shulker_(.*?).png",r'shulker_side_\1.png',img_path))
