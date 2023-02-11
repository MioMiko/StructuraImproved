from PIL import Image
from os import popen
from re import sub

for img_path in popen(r'ls -1 double_plant_sunflower.png').read().strip('\n').split('\n'):
    main = Image.open(img_path)
    front = Image.open(sub(r'(.*).png',r'\1_front.png',img_path))
    back = Image.open(sub(r'(.*).png',r'\1_back.png',img_path))
    target = Image.new('RGBA',(16,32),(255,255,255,0))
    target.paste(main,(0,0),main)
    target.paste(front,(0,0),front)
    target.save('result/double_plant_sunflower_front.png')
    target = Image.new('RGBA',(16,32),(255,255,255,0))
    target.paste(main,(0,0),main)
    target.paste(back,(0,0),back)
    target.save('result/double_plant_sunflower_back.png')
