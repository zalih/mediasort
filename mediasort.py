#!/usr/bin/env python

# Copyright (c) 2019 Salih Kiliclioglu

# Move image files based on exif datetime to subfolders. Group them by year, month or day.
# If exif datetime is not available, look for datetime in filename.

from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from optparse import OptionParser

import os
import shutil
import re
import sys
import logging

logging.basicConfig(filename='./mediasort.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

output_formats = {
    'YEARLY': "%Y",
    'MONTHLY': "%Y-%m",
    'DAILY': "%Y-%m-%d-%A"
}
EXIF_DATETIME = "%Y:%m:%d %H:%M:%S"
FILENAME_DATETIME = "%Y%m%d_%H%M%S"
DEFAULT_SOURCE_FOLDER = "."
DEFAULT_TARGET_FOLDER = "."
DEFAULT_VIDEO_FOLDER = "video"

output_format = ""
filename_pattern = FILENAME_DATETIME
video_subfolder = DEFAULT_VIDEO_FOLDER
opt_recursion = None
recursion_level = 0  # type: int
opt_simulate = True
opt_single = True
loglevel = ""


def get_field(exif, field):
    for (k, v) in exif.iteritems():
        if TAGS.get(k) == field:
            return v


def make_foldername(date_str, pattern):
    global output_format
    if date_str:
        image_datetime = datetime.strptime(date_str, pattern)
        date_str = image_datetime.strftime(output_format)
        logging.debug("Make Foldername: " + date_str)
    return date_str


def get_date_from_filename(name):
    date_str = None
    filename_matches = re.search(r"(\d{8}_\d{6})", name)
    if filename_matches:
        date_str = filename_matches.group()
    return make_foldername(date_str, FILENAME_DATETIME)


def get_date_from_exif(exif_data):
    date_str = get_field(exif_data, 'DateTime')
    return make_foldername(date_str, EXIF_DATETIME)


def create_target_folder(output_folder, folder_str, video=""):
    if not os.path.exists(os.path.join(output_folder, folder_str)):
        if not opt_simulate:
            # os.makedirs(os.path.join(output_folder, folder_str))
            logging.debug("Image Folder created: " + os.path.join(output_folder, folder_str))
    if not os.path.exists(os.path.join(output_folder, folder_str, video)):
        if not opt_simulate:
            # os.makedirs(os.path.join(output_folder, folder_str, video))
            logging.debug("Video Folder created: " + os.path.join(output_folder, folder_str, video))
    return os.path.join(output_folder, folder_str)


def move_file(filename, source_folder, target_folder, subfolder_name, video=""):
    create_target_folder(target_folder, subfolder_name, video)

    if not opt_simulate:
        # shutil.move(os.path.join(source_folder, filename),
        #            os.path.join(target_folder, video, filename))
        logging.info(
            os.path.join(source_folder, filename) + ": moving to " +
            os.path.join(target_folder, subfolder_name, video, filename))
    else:
        logging.info("Simulation: " +
                     os.path.join(source_folder, filename) + ": moving to " +
                     os.path.join(target_folder, subfolder_name, video, filename))


def move_video_file(filename, source, target):
    global DEFAULT_VIDEO_FOLDER
    logging.debug("Video file: " + filename)
    subfolder_name = get_date_from_filename(filename)
    if subfolder_name:
        move_file(filename, source, target, subfolder_name, DEFAULT_VIDEO_FOLDER)
    else:
        logging.warning(os.path.join(source, filename) + ": Can't get date from filename ")
    return


def move_other_file(filename, source, output):
    logging.debug("Other file: " + filename)
    subfolder_name = get_date_from_filename(filename)
    if subfolder_name:
        move_file(filename, source, output, subfolder_name)
    else:
        logging.warning(os.path.join(source, filename) + ": Can't get date from filename ")
    return


def move_exif_file(exif_file, filename, source, output):
    logging.debug("EXIF file: " + filename)
    exif_data = exif_file._getexif()
    if exif_data:
        subfolder_name = get_date_from_exif(exif_data)
        if subfolder_name:
            move_file(filename, source, output, subfolder_name)
        else:
            move_other_file(filename, source, output)
    else:
        move_other_file(filename, source, output)
    return


def check_match(regex_pattern, str):
    match = False
    filename, extension = None, None
    filename_matches = re.finditer(regex_pattern, str, re.UNICODE)
    for match in filename_matches:
        filename, extension = match.groups()
    if filename and extension:
        match = True
    return match


def scan_files(source, output, max_recursion_level):
    global recursion_level
    global loglevel

    filename_regex = r"(?P<filename>.*)\.(?P<extension>JPG|jpg|jpeg|BMP|bmp)"
    filename_regex_video = r"(?P<filename>.*)\.(?P<extension>MPG|mpg|MOV|mov|AVI|avi|MPEG|mpeg|MP4|mp4)"
    filename_regex_other = r"(?P<filename>.*)\.(?P<extension>tiff|tif|TIF|PNG|png)"

    recursion_level += 1
    logging.debug("Recursion Level: " + str(recursion_level) + "/" + str(opt_recursion))

    for filename in os.listdir(source):
        logging.debug("Checking: " + filename)
        if os.path.isdir(os.path.join(source, filename)) and opt_recursion:
            logging.debug(
                filename + " is a folder. " + "Max level " + str(max_recursion_level) + " Current level " + str(
                    recursion_level))
            if max_recursion_level == 0 or max_recursion_level >= recursion_level:
                if not opt_single:
                    output = os.path.join(source, filename)
                scan_files(os.path.join(source, filename), output, recursion_level)

        if check_match(filename_regex, filename):
            with open(os.path.join(source, filename), 'rb') as file:
                image_file = Image.open(file)
                move_exif_file(image_file, filename, source, output)

        if check_match(filename_regex_video, filename):
            move_video_file(filename, source, output)

        if check_match(filename_regex_other, filename):
            move_other_file(filename, source, output)
    recursion_level -= 1
    return

def main(argv):
    # cli parameter defaults
    global opt_recursion
    global opt_simulate
    global opt_single
    global loglevel
    global output_format
    global filename_pattern
    global DEFAULT_SOURCE_FOLDER
    global DEFAULT_TARGET_FOLDER

    parser = OptionParser()
    parser.add_option("-i", "--input", "--source", type="string", dest="source", default=DEFAULT_SOURCE_FOLDER,
                      help="Read from folder SOURCE. Default = current dir")

    parser.add_option("-o", "--output", "--target", type="string", dest="target",
                      help="Write all files to a single location = TARGET. If not specified = source dir of file")

    parser.add_option("-r", "--recursive", "--recursionlevel", type="int", dest="level",
                      help="Levels of subfolders to scan. 0 = unlimited")

    parser.add_option("-g", "--groupby", type="string", dest="group", default="MONTHLY",
                      help="GROUP = YEARLY|MONTHLY|DAILY. Default = MONTHLY")

    parser.add_option("-s", "--simulate", action="store_true", dest="simulate",
                      help="Simulation mode. No files will be moved")

    parser.add_option("-l", "--loglevel", type="string", dest="loglevel",
                      help="LOGLEVEL = ERROR|WARNING|INFO|DEBUG")

    (options, args) = parser.parse_args()
    if options.loglevel:
        numeric_loglevel = getattr(logging, options.loglevel.upper(), None)
        if not isinstance(numeric_loglevel, int):
            logging.error('Invalid log level: %s' % options.loglevel)
        else:
            logging.getLogger().setLevel(numeric_loglevel)
    source_folder = options.source
    output_folder = options.target
    opt_recursion = options.level
    opt_simulate = options.simulate
    output_format = output_formats[options.group]

    logging.debug("Source:" + source_folder)
    if output_folder:
        logging.debug("Target:" + output_folder)
    else:
        output_folder = DEFAULT_TARGET_FOLDER
        opt_single = False
    if opt_recursion:
        logging.debug("Recursion:" + str(opt_recursion))

    scan_files(source_folder, output_folder, opt_recursion)


if __name__ == "__main__":
    logging.info("mediasort.py started")
    main(sys.argv[1:])
