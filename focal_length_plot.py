import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS
from matplotlib import pyplot as plt

# ---------------------------------------------
# Average Focal Length Calculator
# This script will recursively search all folders in the current directory
# and pull their exif data to determine the focal length (if reported) for the image.
# This is a simple way to determine which lens or zoom length you use most!
# 
# NOTE: Does NOT work with raw files, and only tested with JPG files from Fuji cameras.
# To use, run with "python3 average_focal.py" from the directory with all your photos.
# Must have matplotlib for Python installed. You can install with pip3, should be "pip3 install matplotlib"
# ---------------------------------------------

#options
ignore_raw = False
ignore_jpeg = False
ignore_duplicates = True
image_messages = False
directory_messages = True
error_messages = False
#script directory to start from
ROOT = os.getcwd()
directories = [ROOT]
#if you have folders you don't want included, put them in here
excluded_directories = []

#here we'll store the counts as {focal_length : count}
focal_counts = {}

def is_image(img_path):
    # print("checking is image")
    try:
        Image.open(img_path).close()
    except IOError:
        return False
    return True

def get_focal_length(img_path):
    # print(f"getting focal length of {img_path}")
    img = Image.open(img_path)
    #some exif data is seperated out into ifd? I don't know
    #lifted from Pillow documentation, including the hex address
    exif_data = img.getexif()
    ifd_data = exif_data.get_ifd(0x8769)

    for tag_id in ifd_data:
        tag = TAGS.get(tag_id, tag_id)
        content = ifd_data.get(tag_id)
        #the tag ID for focal length
        if(tag_id == 37386):
            # print(f'{tag:25}: {content}')
            img.close()
            return content
    #unknown
    img.close()
    return "unknown"

def print_exif_data(img_path):
    img = Image.open(img_path)
    exif_data = img.getexif()
    # ifd_data = exif_data.get_ifd(0x8769)
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        content = exif_data.get(tag_id)
        print(f'{tag:25}: {content}')
    img.close()

def process_directory(dir):
    with os.scandir(dir) as folder:
        for item in folder:

            if(item.is_dir()):
                if(error_messages): print(f"ERROR: {item.name} is a directory")
                #if not hidden or excluded, add to list of directories to search (travel down tree)
                if (not item.name.startswith(".") and not item.name in excluded_directories):
                    directories.append(item.path)
                continue        
            if(not item.is_file()):
                if(error_messages): print(f"ERROR: {item.name} is not a file")
                continue
            if(not is_image(item.path)):
                if(error_messages): print(f"ERROR: {item.name} is not an image")
                continue
            
            if(image_messages):
                print(f"Processing {item.name}")
            fl = get_focal_length(item.path)

            #add one to dictionary key, or if it doesn't exist initialize to 0
            #and add one
            focal_counts[fl] = focal_counts.get(fl, 0) + 1

while (len(directories)):
    if (directory_messages):
        print(f"Processing directory {directories[0]}")
    process_directory(directories[0])
    directories.pop(0)

focal_counts = sorted(focal_counts.items())
length = len(focal_counts)
#y values of bar graph
plt.bar(range(length), [val[1] for val in focal_counts])
#x labels
plt.xticks(range(length), [val[0] for val in focal_counts])
plt.show()