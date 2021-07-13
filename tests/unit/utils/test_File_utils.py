import os
import shutil
from unittest import TestCase

from osbot_utils.utils.Files import temp_folder, path_combine

from cdr_plugin_folder_to_folder.utils.file_utils import FileService
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
    )

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
        assert 3 == len(self.file_service.files_in_folder(FIXTURE_DIR))

    def test_base64encode(self):
        assert "cGxlYXN1cmUuCg==" == self.file_service.base64encode(path_combine(FIXTURE_DIR, "pleasure"))
        assert "bGVhc3VyZS4K" == self.file_service.base64encode(path_combine(FIXTURE_DIR, "leasure"))
        assert "ZWFzdXJlLgo=" == self.file_service.base64encode(path_combine(FIXTURE_DIR, "easure"))

    def test_base64decode(self):
        decoded = self.file_service.base64decode("cGxlYXN1cmUu")
        assert decoded == b"pleasure."
        decoded = self.file_service.base64decode("bGVhc3VyZS4=")
        assert decoded == b"leasure."
        decoded = self.file_service.base64decode("ZWFzdXJlLg==")
        assert decoded == b"easure."
        decoded = self.file_service.base64decode("YXN1cmUu")
        assert decoded == b"asure."
        decoded = self.file_service.base64decode("c3VyZS4=")
        assert decoded == b"sure."



