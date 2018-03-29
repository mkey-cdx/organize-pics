#!/usr/bin/env python3

import os
import logging
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from glob import glob
from PIL import Image
from shutil import copy2
from time import localtime

WORKING_DIR = os.path.dirname(__file__)
EXIF_DATETIME = 36867

# Get config data.
config = ConfigParser()
config_file = os.path.join(WORKING_DIR, 'config.ini')
config.read(config_file)

src_folder = config.get("Config", "src_folder")
dst_folder = config.get("Config", "dst_folder")
file_types = tuple(config.get("Config", "file_types").split(','))
log_file = os.path.join(WORKING_DIR, config.get("Log", "log_file"))

# Set logger config.
logger = logging.getLogger(__name__)
logger.setLevel(config.get("Log", "log_level"))
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
file_handler = RotatingFileHandler(log_file, 'a', 100000, 1)
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Check source folder.
if not os.path.exists(src_folder):
    logger.error("Invalid source path: {}".format(src_folder))
    raise IOError("Invalid source path. Check config.ini")
else:
    logger.debug("Source folder: {}".format(src_folder))
    logger.debug("Destination folder: {}".format(dst_folder))


# Get each type img files in source folder.
pics = []
for file_type in file_types:
    logger.debug("Getting .{} image files.".format(file_type))
    pics.extend(glob("{0}/*.{1}".format(src_folder, file_type)))


for pic in pics:
    # Parse files metadata.
    try:
        year, month = Image.open(pic)._getexif()[EXIF_DATETIME].split(":")[:2]
    except KeyError:
        logger.error("Error getting exif from {}".format(pic))
        logger.error("Falling back to systemfile metadata...")
        metadata = os.stat(pic)
        year = localtime(metadata.st_mtime).tm_year
        month = "{0:0=2d}".format(localtime(metadata.st_mtime).tm_mon)

    # Copy file to destination subfolders.
    dst_sub = "{0}/{1}/{2}".format(dst_folder, year, month)
    dst_pic = dst_sub + "/" + os.path.basename(pic)

    if not os.path.exists(dst_sub):
        os.makedirs(dst_sub)
        logger.info("Created new directory: {}".format(dst_sub))
    elif not os.path.exists(dst_pic):
        copy2(pic, dst_pic)
        logger.info("Copied {0} to {1}".format(pic, dst_pic))
    else:
        logger.info("File already exists: " + dst_pic)
