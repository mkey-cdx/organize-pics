#!/usr/bin/env python3

import os
from glob import glob
from PIL import Image
from time import localtime
from shutil import copy2
from configparser import ConfigParser

EXIF_DATETIME = 36867

# Get config data.
config = ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_file)

src_folder = config.get("Config", "src_folder")
dst_folder = config.get("Config", "dst_folder")

# Check source folder.
if not os.path.exists(src_folder):
    raise IOError("Invalid source path. Check config.ini")

# Get img files in source folder.
for pic in glob("{}/*.jpg".format(src_folder)):

    # Parse files metadata.
    try:
        year, month = Image.open(pic)._getexif()[EXIF_DATETIME].split(":")[:2]
    except KeyError:
        print("Error getting exif from {}".format(pic))
        print("Falling back to systemfile metadata...")
        metadata = os.stat(pic)
        year = localtime(metadata.st_mtime).tm_year
        month = "{0:0=2d}".format(localtime(metadata.st_mtime).tm_mon)

    # Copy file to destination subfolders.
    dst_sub = "{0}/{1}/{2}".format(dst_folder, year, month)
    dst_pic = dst_sub + "/" + os.path.basename(pic)

    if not os.path.exists(dst_sub):
        os.makedirs(dst_sub)
    elif not os.path.exists(dst_pic):
        copy2(pic, dst_pic)
        print("Copied {0} to {1}".format(pic, dst_pic))
    else:
        print("File already exists: " + dst_pic)
