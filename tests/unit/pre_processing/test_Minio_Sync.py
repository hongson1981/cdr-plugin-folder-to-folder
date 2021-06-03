import os
import sys
from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_create, file_copy, files_list, temp_file, file_delete, \
    temp_folder, folder_delete_all

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.metadata.Metadata import Metadata
from cdr_plugin_folder_to_folder.metadata.Metadata_Utils import Metadata_Utils
from cdr_plugin_folder_to_folder.pre_processing.Minio_Sync import Minio_Sync
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging import log_debug
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

class test_Minio_Sync(TestCase):
    test_file = None
    temp_dir  = None
    file_hash = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir      = temp_folder()
        cls.minio_sync    = Minio_Sync()

    @classmethod
    def tearDownClass(cls) -> None:
        folder_delete_all(cls.temp_dir )

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_mount_minio_bucket_as_hd2(self):
        url = ''
        user = ''
        access_toket = ''
        bucket = ''
        retval = self.minio_sync.mount_minio_bucket_as_hd2(url,user,access_toket,bucket)
        assert retval == Minio_Sync.INVALID_PARAMETERS

        user = 'admin'
        access_toket = 'a-token'
        bucket = 'a-bucket'
        retval = self.minio_sync.mount_minio_bucket_as_hd2(url,user,access_toket,bucket)
        assert retval == Minio_Sync.INVALID_MINIO_URL

