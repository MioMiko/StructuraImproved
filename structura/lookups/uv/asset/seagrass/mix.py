from PIL import Image

Image.open('seagrass_doubletall_bottom_a.tga').crop((0,0,16,16)).save('result/seagrass_doubletall_bottom.png')
Image.open('seagrass_doubletall_top_a.tga').crop((0,0,16,16)).save('result/seagrass_doubletall_top.png')
