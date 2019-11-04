import unittest
from mediasort import get_date_from_filename
from mediasort import make_foldername, FILENAME_DATETIME, output_formats



class MyTestCase(unittest.TestCase):
    def test_get_date_from_filename(self):
        self.assertEqual(get_date_from_filename("file-20190222_153422.mp4"), "20190222_153422")
        self.assertEqual(get_date_from_filename("20190222_153422.mp4"), "20190222_153422")
        self.assertEqual(get_date_from_filename("20190222_153422-file.mp4"), "20190222_153422")


    def test_make_foldername(self):
        self.assertEqual(make_foldername("20190218_153425", FILENAME_DATETIME, output_formats['MONTHLY']), "2019-02")
        self.assertEqual(make_foldername("20190218_153425", FILENAME_DATETIME, output_formats['YEARLY']), "2019")


if __name__ == '__main__':
    unittest.main()
