#!/usr/bin/python3

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
os.chdir(src_folder)
pics = glob.glob("*.jpg")

for pic in pics:
    # Parse files metadata.
    metadata = os.stat(pic)
    year = time.localtime(metadata.st_mtime).tm_year
    month = time.localtime(metadata.st_mtime).tm_mon
    
    # Copy file to destination subfolders.
    dst_sub = "{0}/{1}/{2}".format(dst_folder, str(year), str(month))
    if not os.path.exists(dst_sub):
        os.makedirs(dst_sub)
    elif not os.path.exists(dst_sub + "/" + pic):
        shutil.copy2(pic, dst_sub)
        print("Copied " + pic)
    else:
        print("File already exists: " + pic)
