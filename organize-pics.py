#!/usr/bin/env python3

import os
import logging
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from glob import glob
from PIL import Image
from shutil import copy2
from time import localtime

EXIF_DATETIME = 36867


class Config:
    CWD = os.path.dirname(__file__)

    def __init__(self):
        config = ConfigParser()
        config_file = os.path.join(self.CWD, 'config.ini')
        config.read(config_file)

        self.src_folder = config.get("Config", "src_folder")
        self.dst_folder = config.get("Config", "dst_folder")
        self.file_types = tuple(config.get("Config", "file_types").split(','))
        self.log_file = os.path.join(self.CWD, config.get("Log", "log_file"))
        self.log_level = config.get("Log", "log_level")

    def getLogger(self, caller, file, level):
        logger = logging.getLogger(caller)
        logger.setLevel(level)

        stream_handler = logging.StreamHandler()
        logger.addHandler(stream_handler)

        file_handler = RotatingFileHandler(file, 'a', 100000, 1)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger


# Get config data.
config = Config()

# Set logger config.
logger = config.getLogger(__name__, config.log_file, config.log_level)

# Check source folder.
try:
    assert(os.path.exists(config.src_folder)), \
          "Invalid source path. Check config.ini"
except AssertionError as ex:
    logger.critical(ex)
    raise ex

logger.debug("Source folder: {}".format(config.src_folder))
logger.debug("Destination folder: {}".format(config.dst_folder))

# Get each type img files in source folder.
pics = []
for file_type in config.file_types:
    logger.debug("Getting .{} image files.".format(file_type))
    pics.extend(glob("{}/*.{}".format(config.src_folder, file_type)))


for pic in pics:
    # Parse files metadata.
    try:
        year, month = Image.open(pic)._getexif()[EXIF_DATETIME].split(":")[:2]
    except KeyError:
        logger.error("Error getting exif from {}. "
                     "Falling back to systemfile metadata...".format(pic))
        metadata = os.stat(pic)
        year = localtime(metadata.st_mtime).tm_year
        month = "{0:0=2d}".format(localtime(metadata.st_mtime).tm_mon)

    logger.debug("Exif metadata: year:{} month{}".format(year, month))

    # Copy file to destination subfolders.
    dst_sub = "{}/{}/{}".format(config.dst_folder, year, month)
    dst_pic = dst_sub + "/" + os.path.basename(pic)

    if not os.path.exists(dst_sub):
        os.makedirs(dst_sub)
        logger.info("Created new directory: {}".format(dst_sub))
    elif not os.path.exists(dst_pic):
        copy2(pic, dst_pic)
        logger.info("Copied {} to {}".format(pic, dst_pic))
    else:
        logger.info("File already exists: " + dst_pic)
