import os
import sys
from unittest import TestCase

from osbot_utils.utils.Files import files_list, temp_file, file_copy, file_delete

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

class test_Pre_Processor_API_functions(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_file     = temp_file(contents='Static text so that we have a static hash')

        cls.status        = Status()
        cls.storage       = Storage()

        cls.test_file     = temp_file(contents='Sample test file')
        if len(files_list(cls.storage.hd1())) == 0:
            file_copy(cls.test_file, cls.storage.hd1())

    @classmethod
    def tearDownClass(cls) -> None:
        file_delete  (cls.test_file)

    def test_clear_data_and_status_folders(self):
        retval = clear_data_and_status_folders()
        assert retval['message'] == Pre_Processor.DATA_CLEARED

        assert self.status.get_files_count()            == 0
        assert self.status.get_files_copied()           == 0
        assert self.status.get_files_to_be_copied()     == 0
        assert self.status.get_duplicate_files()        == 0
        assert self.status.get_files_to_process()       == 0
        assert self.status.get_file_left_to_progress()  == 0
        assert self.status.get_completed()              == 0
        assert self.status.get_not_supported()          == 0
        assert self.status.get_failed()                 == 0
        assert self.status.get_in_progress()            == 0

    def test_mark_all_hd2_files_unprocessed(self):
        retval = mark_all_hd2_files_unprocessed()
        assert retval['message'] == Pre_Processor.DATA_RESTORED

        assert self.status.get_files_count()            == 1
        assert self.status.get_files_copied()           == 1
        assert self.status.get_files_to_be_copied()     == 0
        assert self.status.get_duplicate_files()        == 0
        assert self.status.get_files_to_process()       == 0
        assert self.status.get_file_left_to_progress()  == 0
        assert self.status.get_completed()              == 0
        assert self.status.get_not_supported()          == 0
        assert self.status.get_failed()                 == 0
        assert self.status.get_in_progress()            == 0

    def test_pre_process_hd1_data_to_hd2(self):
        retval = clear_data_and_status_folders()
        assert retval['message'] == Pre_Processor.DATA_CLEARED

        retval = pre_process_hd1_data_to_hd2()
        assert retval['message'] == Pre_Processor.PROCESSING_IS_DONE

        assert self.status.get_files_count()            == 1
        assert self.status.get_files_copied()           == 1
        assert self.status.get_files_to_be_copied()     == 0
        assert self.status.get_duplicate_files()        == 0
        assert self.status.get_files_to_process()       == 1
        assert self.status.get_file_left_to_progress()  == 1
        assert self.status.get_completed()              == 0
        assert self.status.get_not_supported()          == 0
        assert self.status.get_failed()                 == 0
        assert self.status.get_in_progress()            == 0

        # verify that status counters do not change if running it second time

        retval = pre_process_hd1_data_to_hd2()
        assert retval['message'] == Pre_Processor.PROCESSING_IS_DONE

        assert self.status.get_files_count()            == 1
        assert self.status.get_files_copied()           == 1
        assert self.status.get_files_to_be_copied()     == 0
        assert self.status.get_duplicate_files()        == 0
        assert self.status.get_files_to_process()       == 1
        assert self.status.get_file_left_to_progress()  == 1
        assert self.status.get_completed()              == 0
        assert self.status.get_not_supported()          == 0
        assert self.status.get_failed()                 == 0
        assert self.status.get_in_progress()            == 0

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

