import unittest
from unittest import mock
from vent import load_sample_list

class TestLoadSampleDirectory(unittest.TestCase):

    def test_load_sample_list(self):
        with mock.patch('os.listdir') as m :
            m.return_value = ['file.dotaligner.out', 'file2.dotaligner.out', 'notafile.out']
            dotaligner_folder = load_sample_list('test')
            self.assertListEqual(['test/file.dotaligner.out', 'test/file2.dotaligner.out'], dotaligner_folder)














