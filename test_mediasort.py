import unittest
import testdata
import mediasort
# import atexit
import os
import logging
import inspect
from PIL import Image

from mediasort import get_date_from_filename, make_foldername_from_date, get_model_from_exif
from mediasort import output_formats, datetime_formats

# atexit.register(testdata.cleanup_test_data)


class MediasortOutput(unittest.TestCase):
    def log_testcase_name(self, param_name):
        logging.info("****** TC: " + param_name + " ******")

    # unit tests
    def test_get_date_from_filename(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        self.assertEqual(get_date_from_filename("file-20190222_153422.mp4", datetime_formats['IOS']), "20190222_153422")
        self.assertEqual(get_date_from_filename("20190222_153422.mp4", datetime_formats['IOS']), "20190222_153422")
        self.assertEqual(get_date_from_filename("20190222_153422-file.mp4", datetime_formats['IOS']), "20190222_153422")

    def test_make_foldername(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        self.assertEqual(make_foldername_from_date("20190218_153425", datetime_formats['IOS']['datetime'], output_formats['MONTHLY']),
                         "2019-02")
        self.assertEqual(make_foldername_from_date("20190218_153425", datetime_formats['IOS']['datetime'], output_formats['YEARLY']),
                         "2019")
        self.assertEqual(make_foldername_from_date("19750517_153425", datetime_formats['IOS']['datetime'], output_formats['DAILY']),
                         "1975-05-17-Sat")

    # system tests
    def test_get_model_from_exif(self):
        testdata.create_test_data()
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        with open(os.path.join("source", "IMG_4810.jpeg"), 'rb') as exif_file:
            image_file = Image.open(exif_file)
            exif_data = image_file._getexif()
            self.assertEqual(get_model_from_exif(exif_data), "iPhone X")
        testdata.cleanup_test_data()

    def test_monthly_output(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 0, output_formats['MONTHLY'])
        self.assertTrue(os.path.exists("source"))
        self.assertTrue(os.path.exists(os.path.join("target", "2019-08")))
        self.assertTrue(os.path.exists(os.path.join("target", "1975-05", "video")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975-05", "video", "file-19750517_091500.mp4")))
        self.assertTrue(os.path.isfile(os.path.join("target", "2019-08", "IMG_4810.jpeg")))
        testdata.cleanup_test_data()

    def test_other_output(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 0, output_formats['MONTHLY'])
        self.assertTrue(os.path.exists(os.path.join("target", "2019-06", "other")))
        self.assertTrue(os.path.isfile(os.path.join("target", "2019-06", "other", "IMG_20190610_190809.JPG")))
        testdata.cleanup_test_data()

    def test_no_model_in_exif(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 0, output_formats['MONTHLY'])
        self.assertTrue(os.path.exists(os.path.join("target", "2020-05", "other")))
        self.assertTrue(os.path.isfile(os.path.join("target", "2020-05", "other", "IMG_20200506_125846.jpg")))
        testdata.cleanup_test_data()

    def test_yearly_output(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 0, output_formats['YEARLY'])
        self.assertTrue(os.path.exists(os.path.join("target", "2019")))
        self.assertTrue(os.path.exists(os.path.join("target", "1975")))
        self.assertTrue(os.path.isfile(os.path.join("target", "2019", "IMG_4810.jpeg")))
        self.assertTrue(os.path.isfile(os.path.join("target", "2019", "other", "IMG_20190610_190809.JPG")))
        testdata.cleanup_test_data()

    def test_daily_output(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 0, output_formats['DAILY'])
        self.assertTrue(os.path.exists(os.path.join("target", "1975-05-17-Sat")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975-05-17-Sat", "video", "file-19750517_091500.mp4")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975-05-17-Sat", "video", "file-19750517_091500_1.mp4")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975-05-17-Sat", "video", "file-19750517-091500.mp4")))
        testdata.cleanup_test_data()

    def test_recursion_lvl1(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 1, output_formats['YEARLY'])
        self.assertTrue(os.path.exists(os.path.join("target", "1975")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975", "video", "file11-19750517_091500.mp4")))
        self.assertFalse(os.path.isfile(os.path.join("target", "1975", "video", "file21-19750517_091500.mp4")))
        self.assertFalse(os.path.isfile(os.path.join("target", "1975", "video", "file31-19750517_091500.mp4")))

        testdata.cleanup_test_data()

    def test_recursion_lvl2(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 2, output_formats['YEARLY'])
        self.assertTrue(os.path.exists(os.path.join("target", "1975")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975", "video", "file11-19750517_091500.mp4")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975", "video", "file21-19750517_091500.mp4")))
        testdata.cleanup_test_data()

    def test_recursion_lvl3(self):
        self.log_testcase_name(inspect.currentframe().f_code.co_name)
        testdata.create_test_data()
        mediasort.scan_files("source", "target", 3, output_formats['YEARLY'])
        self.assertTrue(os.path.exists(os.path.join("target", "1975")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975", "video", "file11-19750517_091500.mp4")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975", "video", "file21-19750517_091500.mp4")))
        self.assertTrue(os.path.isfile(os.path.join("target", "1975", "video", "file31-19750517_091500.mp4")))
        testdata.cleanup_test_data()


if __name__ == '__main__':
    logging.basicConfig(filename='./test_mediasort.log', format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='w', level=logging.INFO)

    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(MediasortOutput)
    unittest.TextTestRunner(verbosity=2).run(suite)
