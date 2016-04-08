import time
import math
from os import listdir
from os.path import isfile, join, splitext
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import numbasom as ns
import pyprind
import ntpath
import numpy as np
import random

def save_image_timestamp(image, path, filename='image_', extension='png'):
    timestamp = str(int(time.time()))
    image.save(path+"/"+filename+timestamp+"."+extension)

def images_paths(path):
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


def patch_coordinates(image, multiplier, patch_size):
    patch_x = patch_size[0]
    patch_y = patch_size[1]
    size = image.size
    min_divs = get_min_divisions(image, patch_x, patch_y)
    divs = (int(min_divs[0]*multiplier), int(min_divs[1]*multiplier))
    x = cutting_coords(patch_x, size[0], divs[0])
    y = cutting_coords(patch_y, size[1], divs[1])
    return x, y, patch_size

def get_min_divisions(image, patch_x, patch_y):

    def min_divisions(patch_size, image_size):
        min_divs = image_size/patch_size
        if min_divs.is_integer():
            return int(min_divs)
        else:
            return math.ceil(min_divs)
    size = image.size
    return (min_divisions(patch_x, size[0]),min_divisions(patch_y, size[1]))


def cutting_coords(len_piece, total_len, no_divisions):
    coords = []
    offset = get_offset(len_piece, total_len, no_divisions)
    for i in range(no_divisions-1):
        coords.append(round(i*offset))
    coords.append(total_len-len_piece)
    return coords

def get_offset(len_piece, total_len, no_divisions):
    return len_piece - (((no_divisions * len_piece) - total_len)/(no_divisions-1))

def plot_patches(image, coords, sizex, sizey):
    fig = plt.figure(figsize = (sizex,sizey))
    ax = fig.add_subplot(1,1,1)
    ax.imshow(image)
    cx = list(coords[0])
    cy = list(coords[1])
    cx.append(image.size[0])
    cy.append(image.size[1])
    ax.set_xticks(cx)
    ax.set_yticks(cy)
    for x in coords[0]:
        for y in coords[1]:
            ax.add_patch(ptc.Rectangle((x, y), coords[2][0], coords[2][1], fill=None))


def get_all_vectors(path, patch_size, multiplier, rot_angle=360):
    
    image_paths = images_paths(path)
    vectors = []
    bar = pyprind.ProgBar(len(image_paths), bar_char='█', width=50, title="Converting images to vectors")
    for path in image_paths:
        img = Image.open(path)
        #rotated_images = get_rotated_images(img, rot_angle)
        #for simg in rotated_images:
        patch_coords = patch_coordinates(img, multiplier, patch_size)
        tempvec = patches_to_vector(img, patch_coords)
        vectors.extend(tempvec)
        bar.update()
    return np.asarray(vectors)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def patches_to_vector(image, patches):
    regions = []
    for x in patches[0]:
        for y in patches[1]:
            box = (x, y, x+patches[2][0], y+patches[2][1])
            file = path_leaf(image.filename)
            f, e = splitext(file)
            region = image.crop(box)
            vec = image_to_vector(region)
            regions.append(vec)
    return regions


def patches_to_images(path, image, patches, extension="JPEG"):
    for x in patches[0]:
        for y in patches[1]:
            box = (x, y, x+patches[2][0], y+patches[2][1])
            file = path_leaf(image.filename)
            f, e = splitext(file)
            region = image.crop(box)
            savepath = path+f+"_"+str((x,y))+e
            region.save(savepath, extension)
    return regions


def image_to_vector(image):
    X,Y = image.size
    if image.mode != 'L':
        image = image.convert('L')
    arr = np.asarray(image)
    X,Y = arr.shape
    return arr.reshape(X*Y)

def lattice_image(lattice, patch_size):
    """Displays the pixels in the lattice"""
    X,Y,Z = lattice.shape
    px = patch_size[0]
    py = patch_size[1]
    image_size_x = px*X
    image_size_y = py*Y
    print ("Image size: %ix%i pixels" %(image_size_x, image_size_y))
    final_image = Image.new('L',(image_size_x, image_size_y))
    for y in range(Y):
        for x in range(X):
            vec = lattice[x][y]
            x_coord = x*px
            y_coord = y*py
            box = (x_coord, y_coord, x_coord+px, y_coord+py)
            newimg = vector_to_image(vec, patch_size, 255)
            final_image.paste(newimg, box)
    return final_image

def vector_to_image(vec, img_size, mult):
    new_img = Image.new('L',img_size)
    pix = new_img.load()
    X, Y = img_size
    #print ("Size: %ix%i" %(X,Y))
    for y in range(Y):
        for x in range(X):
            index = x+y*X
            pix[x,y] = int(vec[index]*mult)
    return new_img


def create_thumbnails(target_width, offsetX, offsetY, images, limit=0):
    if limit==0:
        no_images = len(images)
    else:
        no_images = limit
    X, Y = images[0].size
    
    #this will define the final image size and number of rows and columns
    
    #print ("Number of images: %i" %no_images)
    #print ("Image size: %ix%i" %(X, Y))
    no_columns = target_width//(X+offsetX)
    column_remainder = target_width%(X+offsetX)

    #print ("\nNumber of columns: %i" %no_columns)
    #print ("Column remainder: %i" %column_remainder)
    rem_offset = column_remainder/no_columns
    #print ("Remaining offset: %f\n" %rem_offset)
    
    no_rows = math.ceil(no_images/no_columns)
    #print ("Number of rows: %i" %no_rows)
    potential = no_rows*no_columns
    #print ("Potentially storing %i images" %potential)
    
    final_image = Image.new('RGB',(target_width, no_rows*(Y+offsetY)), (255,255,255))
    #print ("Final image size: %s" %str(final_image.size))
    
    offX = [round(i*(rem_offset+offsetX+X)) for i in range(no_columns)]
    offY = [i*(Y+offsetY) for i in range(no_rows)]
    
    for j, y in enumerate(offY):
        for i, x in enumerate(offX):
            box = (x, y, x+X, y+Y)
            index = j*len(offX) + i
            if limit==0:
                if index<len(images):
                    img = images[index]
                    final_image.paste(img, box)
            else:
                if index<limit:
                    random_index = random.randint(0,len(images)-1)
                    img = images[random_index]
                    final_image.paste(img, box)
    
    return final_image


def rotate_image(image, rotation):
    im_new = image.convert('RGBA')
    im_rotated = im_new.rotate(rotation, expand=1)
    # a white image same size as rotated image
    white = Image.new('RGBA', im_rotated.size, (255,)*4)
    # create a composite image using the alpha layer of rot as a mask
    composite = Image.composite(im_rotated, white, im_rotated)
    # convert to original format
    final = composite.convert(image.mode)
    return final

def rotated_images(img, rot_angle):
    rotations = np.arange(0,360, rot_angle)
    return [rotatedImage(img, angle) for angle in rotations]


def get_thumbnail_size(image_size, target_width, offsetX, offsetY, limit=0):
    if limit==0:
        no_images = len(images)
    else:
        no_images = limit
    X, Y = image_size  
    no_columns = target_width//(X+offsetX)
    no_rows = math.ceil(no_images/no_columns)
    return target_width, no_rows*(Y+offsetY)


def create_elements_map(som_size, patch_size, vectors, projected_dict, target_width, no_images, offsetX=10, offsetY=10):

    X, Y = get_thumbnail_size(patch_size, target_width, offsetX, offsetY, limit=no_images)
    final_image = Image.new('L',(som_size[0]*X, som_size[1]*Y), 255)
    bar = pyprind.ProgBar(som_size[0]*som_size[1], bar_char='█', width=50, title="Creating the image")

    for y in range(som_size[1]):
        for x in range(som_size[0]):
            v = projected_dict[(x,y)]
            projected = ns.get_projected_vectors(vectors, v)
            vector_len = len(projected)
            #print ("Cell: %i,%i | No vectors: %i" %(x, y, vector_len))
            randoms = np.random.randint(0,vector_len,no_images) 
            images = [vector_to_image(projected[randoms[i]], patch_size, 1) for i in range(no_images)]
            thumb = create_thumbnails(target_width, offsetX, offsetY, images, no_images)
            box = (x*X, y*Y, x*X+X, y*Y+Y)
            final_image.paste(thumb, box)
            bar.update()
    return final_image