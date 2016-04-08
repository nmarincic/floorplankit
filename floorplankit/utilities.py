import time

def save_image_timestamp(image, path, filename='image_', extension='png'):
    timestamp = str(int(time.time()))
    image.save(path+"/"+filename+timestamp+"."+extension)

def get_file_paths(path):
    image_paths = []
    file_paths = [path+f for f in listdir(path) if isfile(join(path, f))]
    for path in file_paths:
        try:
            im = Image.open(path)
            #print (file, im.format, "%dx%d" %im.size, im.mode)
            image_paths.append(path)
        except IOError:
            pass
    return image_paths