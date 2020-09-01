#!/usr/bin/env python
import glob
import os
import shutil


def cleanup_test_data():
    try:
        shutil.rmtree(os.path.join("source"), ignore_errors=True)
        shutil.rmtree("target", ignore_errors=True)
    except IOError:
        print IOError


def create_test_data():
    if os.path.exists("source"):
        cleanup_test_data()

    os.makedirs(os.path.join("source", "lvl11", "lvl21", "lvl31"))
    os.makedirs(os.path.join("source", "lvl12", "lvl22", "lvl32"))
    os.makedirs(os.path.join("source", "lvl13", "lvl23", "lvl33"))
    os.makedirs(os.path.join("source", "@eaDir", "IMG_20190610_190809.JPG"))
    os.makedirs(os.path.join("target"))

    os.close(os.open(os.path.join("source", "file-19750517_091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "file-19750517_091500_1.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "file-19750517-091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl11", "file11-19750517_091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl11", "lvl21", "file21-19750517_091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl11", "lvl21", "lvl31", "file31-19750517_091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl12", "file12-19750517-091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl12", "lvl22", "file22-19750517-091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl12", "lvl22", "lvl32", "file32-19750517-091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl13", "file13-19750517-091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl13", "lvl23", "file23-19750517-091500.mp4"), os.O_CREAT))
    os.close(os.open(os.path.join("source", "lvl13", "lvl23", "lvl33", "file33-19750517-091500"), os.O_CREAT))

    for testfile in glob.glob(os.path.join("testdata", "*")):
        shutil.copy2(testfile, "source")
    return

