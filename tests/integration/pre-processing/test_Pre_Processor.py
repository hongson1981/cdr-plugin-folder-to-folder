import os
import sys
from unittest import TestCase

from cdr_plugin_folder_to_folder.pre_processing.Pre_Processor import Pre_Processor
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging import log_debug

from cdr_plugin_folder_to_folder.pre_processing.Status import Status
from cdr_plugin_folder_to_folder.storage.Storage import Storage

from cdr_plugin_folder_to_folder.api.routes.Pre_Processor import \
    DIRECTORY                           ,\
    DOWNLOAD_URL                        ,\
    pre_process_hd1_data_to_hd2         ,\
    clear_data_and_status_folders       ,\
    mark_all_hd2_files_unprocessed      ,\
    pre_process_a_folder                ,\
 	download_and_pre_process_a_zip_file

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

class test_Pre_Processor(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.status        = Status()
        cls.storage       = Storage()

    def test_pre_process_hd1_data_to_hd2(self):
        retval = pre_process_hd1_data_to_hd2()
        assert retval['message'] == Pre_Processor.PROCESSING_IS_DONE

    def test_clear_data_and_status_folders(self):
        retval = clear_data_and_status_folders()
        assert retval['message'] == Pre_Processor.DATA_CLEARED

    def test_mark_all_hd2_files_unprocessed(self):
        retval = mark_all_hd2_files_unprocessed()
        assert retval['message'] == Pre_Processor.DATA_RESTORED

    def test_pre_process_a_folder(self):
        item = DIRECTORY()
        item.folder = self.storage.hd1()
        retval = pre_process_a_folder(item)
        assert retval['message'] == f"Directory {self.storage.hd1()} added"

    def test_download_and_pre_process_a_zip_file(self):
        item = DOWNLOAD_URL()
        item.url = "http://google.com/"
        retval = download_and_pre_process_a_zip_file(item)
        assert retval['message'] == "File is not a zip file"

