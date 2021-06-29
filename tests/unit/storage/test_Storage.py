from os.path import abspath
from unittest import TestCase

import pytest
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import path_combine, temp_file, file_exists, file_contents, file_name, \
    file_contents_as_bytes
from osbot_utils.utils.Misc import random_text, list_set

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.processing.Loops import Loops
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.testing.Temp_Config import Temp_Config


class test_Storage(Temp_Config):

    def setUp(self) -> None:
        self.config        = Config()
        self.local_storage = Storage()

    def test_hd1_hd2_hd3(self):
        assert self.local_storage.hd1() == abspath(self.config.hd1_location)
        assert self.local_storage.hd2() == abspath(self.config.hd2_location)
        assert self.local_storage.hd3() == abspath(self.config.hd3_location)

    def test_hd1_add_file(self):
        test_file      = temp_file(contents=random_text())
        test_file_name = file_name(test_file)
        file_in_hd1    = self.storage.hd1_add_file(test_file)
        assert file_exists(file_in_hd1)
        assert file_contents(file_in_hd1) == file_contents(test_file)
        assert self.storage.hd1_file_path(test_file_name) == file_in_hd1

    def test_hd1_files(self):
        new_files = self.add_test_files(count=2)
        hd1_files = self.storage.hd1_files()
        assert len(hd1_files) >= len(new_files)
        assert new_files[0] in hd1_files
        assert new_files[1] in hd1_files

    def test_hd2_metadatas(self):
        self.add_test_files(count=10, text_size=1000, execute_stage_1=True)
        metadatas = self.storage.hd2_metadatas()
        assert list_set(metadatas[0]) == [ 'adaptation_file_id', 'error', 'f2f_plugin_git_commit', 'f2f_plugin_version', 'file_name', 'hd1_to_hd2_copy_time', 'hd2_to_hd3_copy_time', 'last_update_time', 'original_file_extension', 'original_file_paths', 'original_file_size', 'original_hash', 'original_hash_calculation_time', 'rebuild_file_duration', 'rebuild_file_extension', 'rebuild_file_path', 'rebuild_file_size', 'rebuild_hash', 'rebuild_server', 'rebuild_status', 'sdk_api_version', 'server_header', 'server_version', 'skd_engine_version', 'status_code', 'via_header', 'xml_report_status']


    @pytest.mark.skip("needs more work to be solid")
    def test_hd3_files(self):
        count = 1
        self.add_test_files(count=count, execute_stage_1=True)
        loops     = Loops()
        result    = loops.LoopHashDirectories()
        metadatas = self.storage.hd2_metadatas()
        hd3_files = self.storage.hd3_files()
        metadata  = metadatas[0]
        hd3_file  = hd3_files[0]

        assert result is True
        assert len(hd3_files) == count
        assert len(metadatas) == count
        assert b'Glasswall Processed' in file_contents_as_bytes(hd3_file)
        assert metadata.get('rebuild_status') == 'Completed Successfully'
