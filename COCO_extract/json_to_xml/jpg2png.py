from PIL import Image
import os

directory = r'/media/jason/9400F87F00F8699E/Tommy_TriSDNet/c2l_train/'

for filename in os.listdir(directory): 
    # print("Filename:",filename)
    if filename.endswith(".jpg"): 
        print("JPG:",filename)
        prefix = filename.split(".jpg")[0]
        im = Image.open(directory + filename)
        im.save(directory + prefix+'.png')  
    else: 
        continue

for _file in os.listdir(directory):
    print("_file:",_file)
    if _file.endswith('.jpg'):
        os.remove(directory + _file)