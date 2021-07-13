import os
import shutil
from unittest import TestCase

from osbot_utils.utils.Files import folder_exists, temp_folder, file_exists, folder_temp, folder_delete_all, temp_file, \
    file_copy, create_folder

from cdr_plugin_folder_to_folder.utils.file_utils import FileService
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

class test_File_utils(TestCase):
    #test_folder="./test_data/test_files"
    #new_folder=os.path.join(test_folder, "sample")
    new_folder = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.new_folder = temp_folder()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.new_folder)
        pass

    def setUp(self) -> None:
        self.test_data    = Test_Data()
        self.file_service = FileService()
        self.test_folder  = self.test_data.path_test_files
        self.test_file    = self.test_data.image()
        self.dict_content = { "value": "testing" }

    def test_files_in_folder(self):
        pass





