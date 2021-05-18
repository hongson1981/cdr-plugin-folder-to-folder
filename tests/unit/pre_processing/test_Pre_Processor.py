import os
import sys
from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_create, file_copy, files_list, temp_file, file_delete, \
    temp_folder, folder_delete_all

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.metadata.Metadata import Metadata
from cdr_plugin_folder_to_folder.metadata.Metadata_Utils import Metadata_Utils
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging import log_debug
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

class test_Pre_Processor(TestCase):
    test_file = None
    temp_dir  = None
    file_hash = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_file     = temp_file(contents='Static text so that we have a static hash')
        cls.file_hash     = '500286533bf75d769e9180a19414d1c3502dd52093e7351a0a9b1385d8f8961c'
        cls.temp_dir      = temp_folder()
        file_copy(cls.test_file, cls.temp_dir)
        cls.pre_processor = Pre_Processor()
        Setup_Testing().configure_pre_processor(cls.pre_processor)

    @classmethod
    def tearDownClass(cls) -> None:
        file_delete      (cls.test_file)
        folder_delete_all(cls.temp_dir )
        Metadata(file_hash=cls.file_hash).delete()

    def setUp(self) -> None:
        self.pre_processor.clear_data_and_status_folders()

    def tearDown(self) -> None:
        pass


    def test__init__(self):
        assert folder_exists(self.pre_processor.storage.hd2_data()  )
        assert folder_exists(self.pre_processor.storage.hd2_status())
        #assert folder_exists(self.path_h1)

    def test_file_hash(self):
        assert self.pre_processor.file_hash(self.test_file) == self.file_hash

    def test_process_folder(self):
        path_data   = self.pre_processor.storage.hd2_data()

        filename = os.path.basename(self.test_file)
        folder_to_process = self.pre_processor.prepare_folder(self.temp_dir)
        assert folder_exists(self.temp_dir)
        assert folder_to_process.startswith(self.pre_processor.storage.hd1())
        assert os.path.isdir(folder_to_process)
        assert os.path.isfile(os.path.join(folder_to_process, filename))
        folder_delete_all(folder_to_process)

        assert not os.path.isfile(os.path.join(folder_to_process, filename))

        self.pre_processor.clear_data_and_status_folders()
        self.pre_processor.process_folder(self.temp_dir)
        assert os.path.isdir(folder_to_process)
        assert os.path.isfile(os.path.join(folder_to_process, filename))
        assert len(files_list(path_data  )) == 1

        self.pre_processor.process_folder(self.temp_dir)
        assert len(files_list(path_data  )) == 1

        folder_delete_all(folder_to_process)
        self.pre_processor.clear_data_and_status_folders()

    def test_process_files(self):
        path_data   = self.pre_processor.storage.hd2_data()
        path_status = self.pre_processor.storage.hd2_status()

        assert len(files_list(path_data   )) == 0
        assert len(files_list(path_status )) == 1       # should have the status.json file

        self.pre_processor.process_files()

        pprint('**********: DATA')
        pprint(files_list(path_data  ))
        pprint('**********: STATUS')
        pprint(files_list(path_status))
        pprint('------------------------')
        assert len(files_list(path_data  )) > 0
        assert len(files_list(path_status)) == 1            # should have: status.json

    def test_process_file(self):
        metadata = Metadata(file_hash=self.file_hash)
        assert metadata.exists() is False
        self.pre_processor.process(self.test_file)
        assert metadata.exists() is True

    def test_process_downloaded_zip_file(self):
        retvalue = self.pre_processor.process_downloaded_zip_file("http://google.com/")
        assert retvalue == "File is not a zip file"




