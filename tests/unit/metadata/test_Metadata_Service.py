import os
from unittest                                            import TestCase
from unittest.mock import patch

from osbot_utils.utils.Files                             import file_exists, file_sha256, file_name

from cdr_plugin_folder_to_folder.metadata.Metadata import Metadata
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data
from cdr_plugin_folder_to_folder.metadata.Metadata_Service import Metadata_Service
from cdr_plugin_folder_to_folder.pre_processing.Status import FileStatus
from cdr_plugin_folder_to_folder.storage.Storage import Storage

class test_Metadata_Service(TestCase):

    def setUp(self) -> None:
        self.metadata_service = Metadata_Service()
        self.test_file        = Test_Data().images().pop()
        self.storage          = Storage()
        assert file_exists(self.test_file)

    def test_create_metadata(self):

        metadata  = self.metadata_service.create_metadata(self.test_file)
        assert metadata.delete() is True

        metadata.add_file(self.test_file)
        assert metadata.data == {   'file_name'              : file_name(self.test_file)        ,
                                    'xml_report_status'      : None                             ,
                                    'last_update_time'       : metadata.get_last_update_time()  ,
                                    'status_code'            : None                             ,
                                    'rebuild_server'         : None                             ,
                                    'server_header'          : None                             ,
                                    'via_header'             : None                             ,
                                    'server_version'         : None                             ,
                                    'sdk_api_version'        : None                             ,
                                    'skd_engine_version'     : None                             ,
                                    'adaptation_file_id'     : None                             ,
                                    'error'                  : None                             ,
                                    'original_file_paths'    : [self.test_file]                 ,
                                    'original_hash'          : file_sha256(self.test_file)      ,
                                    'original_hash_calculation_time': metadata.data.get('original_hash_calculation_time') ,
                                    'original_file_extension': '.jpg'                           ,
                                    'original_file_size'     : 97610                            ,
                                    'rebuild_file_path'      : None                             ,
                                    'rebuild_hash'           : None                             ,
                                    'rebuild_status'         : FileStatus.INITIAL               ,
                                    'rebuild_file_extension' : None                             ,
                                    'rebuild_file_size'      : None                             ,
                                    'rebuild_file_duration'  : None                             ,
                                    'f2f_plugin_version'     : None                             ,
                                    'f2f_plugin_git_commit'  : None                             ,
                                    'hd1_to_hd2_copy_time'   : None                             ,
                                    'hd2_to_hd3_copy_time'   : None
                                }

        assert metadata.delete() is True

        metadata  = self.metadata_service.create_metadata(self.test_file)
        self.metadata_service.reset_metadata(self.storage.hd2_data(file_sha256(self.test_file)))
        assert metadata.delete() is True


    def test_file_hash(self):
        hash=self.metadata_service.file_hash(self.test_file)
        assert hash == file_sha256(self.test_file)

    def test_file_hash_metadata(self):
        pass


    # todo: fix test (to be focused on .set_metadata_field() method)
    # @patch('cdr_plugin_folder_to_folder.metadata.Metadata_Elastic.Metadata_Elastic.add_metadata')
    # def test_write_metadata_to_file(self, mock_add_metadata):
    #     expected_metadata = { 'file_name'           : file_name(self.test_file) ,
    #                           'original_file_paths' : [self.test_file]          ,
    #                           'original_hash'       : self.file_hash            ,
    #                           'rebuild_hash'        : None                      ,
    #                           'rebuild_status'      : 'Initial'                 ,
    #                           'xml_report_status'   : None                      ,
    #                           'target_path'         : None                      ,
    #                           'error'               : None                      }
    #     #metadata_folder = temp_folder()
    #     self.test_metadata = Metadata()
    #     self.test_metadata.add_file(self.test_file)
    #     #metadata        = self.test_metadata.data
    #     self.metadata_service.write_metadata_to_file(metadata, metadata_folder)
    #     assert json_load_file(self.metadata_service.get_metadata_file_path()) == expected_metadata
    #     assert mock_add_metadata.mock_calls == [call(expected_metadata)]
    #     #folder_delete_all(metadata_folder)
    #     self.test_metadata.delete()
