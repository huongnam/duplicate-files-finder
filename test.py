from find_duplicate_files import *
import unittest
from os import chdir
from subprocess import getoutput


class TestDuplicateFilesFinder(unittest.TestCase):
    def setUp(self):
        getoutput("mkdir test")
        chdir("test/")
        getoutput("touch emptyfile")
        getoutput("echo samecontent > file1")
        getoutput("echo samecontent > file2")
        getoutput("echo samecontent > file3")
        getoutput("chmod 000 file3")
        getoutput("echo samebytesss > file4")
        getoutput("echo samecontentbutlonger > file5")
        getoutput("echo samecontent2 > hiddenfile1")
        getoutput("echo samecontent2 > hiddenfile2")
        getoutput("ln -s file1 symlink1")
        getoutput("touch file")
        chdir('../')

    def test_scan_files(self):
        out = str(scan_files("test"))
        self.assertNotIn("symlink1", out)
        self.assertIn("file1", out)
        self.assertIn("file2", out)
        self.assertNotIn("file3", out)
        self.assertIn("file4", out)
        self.assertIn("emptyfile", out)

    def test_group_files_by_size(self):
        out = group_files_by_size(scan_files("test"))
        self.assertIn(['/home/vnam/vnam/test/file1',
                      '/home/vnam/vnam/test/file2',
                      '/home/vnam/vnam/test/file4'], out)
        self.assertIn(['/home/vnam/vnam/test/hiddenfile2',
                       '/home/vnam/vnam/test/hiddenfile1'], out)

    def test_group_files_by_content(self):
        out = group_files_by_content(scan_files("test"))
        self.assertIn(['/home/vnam/vnam/test/emptyfile',
                       '/home/vnam/vnam/test/file'], out)
        self.assertIn(['/home/vnam/vnam/test/file1',
                       '/home/vnam/vnam/test/file2',
                       '/home/vnam/vnam/test/file5',
                       '/home/vnam/vnam/test/hiddenfile2',
                       '/home/vnam/vnam/test/hiddenfile1'], out)

    def test_group_files_by_checksum(self):
        out = group_files_by_checksum(scan_files("test"))
        self.assertIn(['/home/vnam/vnam/test/emptyfile',
                       '/home/vnam/vnam/test/file'], out)
        self.assertIn(['/home/vnam/vnam/test/file1',
                       '/home/vnam/vnam/test/file2'],out)
        self.assertIn(['/home/vnam/vnam/test/hiddenfile2',
                       '/home/vnam/vnam/test/hiddenfile1'],out)

    def test_find_duplicate_files(self):
        out = find_duplicate_files(scan_files("test"))
        self.assertIn(['/home/vnam/vnam/test/file1',
                      '/home/vnam/vnam/test/file2'], out)
        self.assertIn(['/home/vnam/vnam/test/hiddenfile2',
                       '/home/vnam/vnam/test/hiddenfile1'], out)

if __name__ == '__main__':
    unittest.main()
