from PIL import Image
from os import popen

for img_path in popen(r'ls -1 *.png').read().strip('\n').split('\n'):
    img = Image.open(img_path)
    target = Image.new('RGBA',(16,32))
    tmp = img.crop((0,0,16,16))
    target.paste(tmp,(0,0),tmp)
    tmp = img.crop((16,0,32,16))
    target.paste(tmp,(0,16),tmp)
    target.save(f'result/{img_path}')
