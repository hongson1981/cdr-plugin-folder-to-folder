from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists

from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data


class test_Test_Data(TestCase):

    def setUp(self) -> None:
        self.test_data = Test_Data()

    def test__init__(self):
        assert folder_exists(self.test_data.path_test_files)

    def test_files(self):
        assert len(self.test_data.files()   ) == 3

    def test_images(self):
        assert len(self.test_data.images()  ) == 1

    def test_pdfs(self):
        assert len(self.test_data.pdfs()    ) == 1