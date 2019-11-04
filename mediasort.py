#!/usr/bin/env python

# Copyright (c) 2019 Salih Kiliclioglu

# Move image files based on exif datetime to subfolders. Group them by year, month or day.
# If exif datetime is not available, look for datetime in filename.
# Video files are moved into a separate subfolder

from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from optparse import OptionParser

import os
import shutil
import re
import sys
import logging

# global variables

# available formats used for output folder creation
output_formats = {
    'YEARLY': "%Y",
    'MONTHLY': "%Y-%m",
    'DAILY': "%Y-%m-%d-%a"
}
# variable to store output folder format
output_format = ""

EXIF_DATETIME = "%Y:%m:%d %H:%M:%S"
FILENAME_DATETIME = "%Y%m%d_%H%M%S"
DEFAULT_SOURCE_FOLDER = "."
DEFAULT_TARGET_FOLDER = "."

# subfolder for video files
DEFAULT_VIDEO_FOLDER = "video"

filename_pattern = FILENAME_DATETIME
video_subfolder = DEFAULT_VIDEO_FOLDER

# variables to store command line options
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
    return make_foldername(date_str, pattern, output_format)


def make_foldername(date_str, pattern, output_pattern):
    if date_str:
        image_datetime = datetime.strptime(date_str, pattern)
        date_str = image_datetime.strftime(output_pattern)
        logging.debug("Make Foldername: " + date_str)
    return date_str


def get_date_from_filename(name):
    date_str = None
    filename_matches = re.search(r"(\d{8}_\d{6})", name)
    if filename_matches:
        date_str = filename_matches.group()
    return date_str


def get_date_from_exif(exif_data):
    date_str = get_field(exif_data, 'DateTime')
    return make_foldername(date_str, EXIF_DATETIME)


def create_target_folder(path):
    if not os.path.exists(path):
        if not opt_simulate:
            None
            # TODO: activate after successful simulation
            # os.makedirs(os.path.join(path))
        logging.debug("Folder created: " + path)
    return


def move_file(filename, source_folder, target_folder, subfolder_name, video=""):
    create_target_folder(os.path.join(target_folder, subfolder_name, video))

    if not opt_simulate:
        # TODO: activate after successful simulation
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
    subfolder_name = make_foldername(get_date_from_filename(filename), FILENAME_DATETIME)
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

    # increase global recursion counter when function entered and decrease before exit
    recursion_level += 1
    logging.debug("Recursion Level: " + str(recursion_level) + "/" + str(opt_recursion))

    for filename in os.listdir(source):
        logging.debug("Checking: " + filename)
        if os.path.isdir(os.path.join(source, filename)) and opt_recursion:
            logging.debug(
                filename + " is a folder. " + "Max level " + str(max_recursion_level) + " Current level " + str(
                    recursion_level))
            if max_recursion_level == 0 or max_recursion_level >= recursion_level:
                # opt_single is true, when an output folder has been specified
                # if no output folder specified, create output folder in the same location as the source file
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
        # no single location for output if no target folder specified
        # set opt_single to false, source file location will be used for outputs
        opt_single = False
    if opt_recursion:
        logging.debug("Recursion:" + str(opt_recursion))

    # start reading the source folder
    scan_files(source_folder, output_folder, opt_recursion)


if __name__ == "__main__":
    logging.basicConfig(filename='./mediasort.log',
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


    logging.info("mediasort.py started")
    main(sys.argv[1:])
