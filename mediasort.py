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

output_formats = {  # available formats used for output folder creation
    'YEARLY': "%Y",
    'MONTHLY': "%Y-%m",
    'DAILY': "%Y-%m-%d-%a"
}

DATETIME_FORMAT_EXIF = "%Y:%m:%d %H:%M:%S"

datetime_formats = {
    'IOS': {'regex': r'\d{8}_\d{6}', 'datetime': '%Y%m%d_%H%M%S'},
    'OTHER': {'regex': r'\d{8}\-\d{6}', 'datetime': '%Y%m%d-%H%M%S'}
}

FILE_EXTENSION_EXIF = 'JPG|jpg|jpeg|BMP|bmp|PNG|png'
FILE_EXTENSION_VIDEO = 'MPG|mpg|MOV|mov|AVI|avi|MPEG|mpeg|MP4|mp4'
FILE_EXTENSION_OTHER = 'tiff|tif|TIF'

DEFAULT_SOURCE_FOLDER = "."
DEFAULT_TARGET_FOLDER = "."

# subfolder for video files
DEFAULT_VIDEO_FOLDER = "video"

# variables to store command line options
opt_recursion = None
recursion_level = 0  # type: int
opt_simulate = False
opt_single = True


def get_field(exif, field):
    for (k, v) in exif.iteritems():
        if TAGS.get(k) == field:
            return v


# date_str = input string
# pattern = source date format to parse date from input
# output_pattern = target date format for output
def make_foldername_from_date(date_str, pattern, output_pattern):
    if date_str:
        image_datetime = datetime.strptime(date_str, pattern)
        date_str = image_datetime.strftime(output_pattern)
        logging.debug("Make Foldername: " + date_str)
    return date_str


def get_date_from_filename(param_name, datetime_format):
    date_str = None
    filename_matches = re.search(r"%s" % datetime_format['regex'], param_name)
    if filename_matches:
        date_str = filename_matches.group()
    return date_str


def get_date_from_exif(exif_data):
    date_str = get_field(exif_data, 'DateTime')
    return date_str


def create_target_folder(path):
    if not os.path.exists(path):
        if not opt_simulate:
            os.makedirs(os.path.join(path))
        logging.debug("Folder created: " + path)
    return


def move_file(filename, source_folder, target_folder, subfolder_name, video=""):
    moved = False
    create_target_folder(os.path.join(target_folder, subfolder_name, video))

    if not opt_simulate:
        try:
            shutil.move(os.path.join(source_folder, filename),
                        os.path.join(target_folder, subfolder_name, video))
            logging.info(
                os.path.join(source_folder, filename) + ": moving to " +
                os.path.join(target_folder, subfolder_name, video))
        except IOError:
            moved = False
        else:
            moved = True
    else:
        logging.info("Simulation: " +
                     os.path.join(source_folder, filename) + ": moving to " +
                     os.path.join(target_folder, subfolder_name, video))
    return moved


def move_video_file(filename, source, target, output_format, datetime_format):
    global DEFAULT_VIDEO_FOLDER
    logging.debug("Video file: " + filename)
    subfolder_name = make_foldername_from_date(get_date_from_filename(filename, datetime_format),
                                               datetime_format['datetime'], output_format)
    if subfolder_name:
        move_file(filename, source, target, subfolder_name, DEFAULT_VIDEO_FOLDER)
    else:
        logging.warning(os.path.join(source, filename) + ": Can't get date from filename ")
    return


def move_other_file(filename, source, output, datetime_format):
    logging.debug("Other file: " + filename)
    subfolder_name = make_foldername_from_date(get_date_from_filename(filename, datetime_format),
                                               datetime_format['regex'], output_format)
    if subfolder_name:
        move_file(filename, source, output, subfolder_name)
    else:
        logging.warning(os.path.join(source, filename) + ": Can't get date from filename ")
    return


def move_exif_file(exif_file, filename, source, output, output_format):
    moved = False
    logging.debug("EXIF file: " + filename)
    exif_data = exif_file._getexif()
    if exif_data:
        subfolder_name = make_foldername_from_date(get_date_from_exif(exif_data), DATETIME_FORMAT_EXIF, output_format)
        if subfolder_name:
            move = move_file(filename, source, output, subfolder_name)
    return moved


def check_match(regex_pattern, str):
    match = False
    filename, extension = None, None
    filename_matches = re.finditer(regex_pattern, str, re.UNICODE)
    for match in filename_matches:
        filename, extension = match.groups()
    if filename and extension:
        match = True
    return match


def scan_files(source, output, max_recursion_level, output_format):
    global recursion_level

    # increase global recursion counter when function entered and decrease before exit
    recursion_level += 1
    logging.debug("Recursion Level: " + str(recursion_level) + "/" + str(max_recursion_level))

    for filename in os.listdir(source):
        logging.debug("Checking: " + filename)
        if os.path.isdir(os.path.join(source, filename)) and max_recursion_level:
            logging.debug(
                filename + " is a folder. " + "Max level " + str(max_recursion_level) + " Current level " + str(
                    recursion_level))
            if max_recursion_level == 0 or max_recursion_level >= recursion_level:
                # opt_single is true, when an output folder has been specified
                # if no output folder specified, create output folder in the same location as the source file
                if not opt_single:
                    output = os.path.join(source, filename)
                scan_files(os.path.join(source, filename), output, max_recursion_level, output_format)

        if check_match(r"(?P<filename>.*)\.(?P<extension>%s)" % FILE_EXTENSION_EXIF, filename):
            with open(os.path.join(source, filename), 'rb') as exif_file:
                image_file = Image.open(exif_file)
                move_exif_file(image_file, filename, source, output, output_format)

        match = False
        for datetime_format in datetime_formats:
            if check_match(r"(?P<filename>%s)\.(?P<extension>%s)" % (datetime_formats[datetime_format]['regex'], FILE_EXTENSION_VIDEO), filename):
                move_video_file(filename, source, output, output_format, datetime_formats[datetime_format])
                match = True
                break
            elif check_match(r"(?P<filename>%s)\.(?P<extension>%s)" % (datetime_formats[datetime_format]['regex'], FILE_EXTENSION_OTHER),
                             filename):
                move_other_file(filename, source, output, output_format, datetime_formats[datetime_format])
                match = True
                break
            elif os.path.isdir(os.path.join(source, filename)):
                logging.debug(os.path.join(source, filename) + ": Is a directory ")
                match = True

        if not match:
            logging.warning(os.path.join(source, filename) + ": Can't get date from exif or filename ")

        recursion_level -= 1
    return


def main(argv):
    global opt_recursion
    global opt_simulate
    global opt_single
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
    scan_files(source_folder, output_folder, opt_recursion, output_format)


if __name__ == "__main__":
    logging.basicConfig(filename='./mediasort.log',
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    logging.info("mediasort.py started")
    main(sys.argv[1:])
