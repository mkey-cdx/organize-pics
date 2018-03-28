#!/usr/bin/env python3

import os
import glob
import time
import shutil
import configparser

# Get config data.
config = configparser.ConfigParser()
config.read("config.ini")

src_folder = config.get("Config", "src_folder")
dst_folder = config.get("Config", "dst_folder")

# Get img files in source folder.
for pic in glob.glob("{}/*.jpg".format(src_folder)):

    # Parse files metadata.
    metadata = os.stat(pic)
    year = time.localtime(metadata.st_mtime).tm_year
    month = time.localtime(metadata.st_mtime).tm_mon

    # Copy file to destination subfolders.
    dst_sub = "{0}/{1}/{2:0=2d}".format(dst_folder, year, month)
    if not os.path.exists(dst_sub):
        os.makedirs(dst_sub)
    elif not os.path.exists(dst_sub + "/" + pic):
        shutil.copy2(pic, dst_sub)
        print("Copied " + pic)
    else:
        print("File already exists: " + pic)