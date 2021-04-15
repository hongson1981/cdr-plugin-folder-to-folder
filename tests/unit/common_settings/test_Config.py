from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, folder_delete_all, file_not_exists, file_exists
from osbot_utils.utils.Misc import list_set

from cdr_plugin_folder_to_folder.common_settings.Config import *

class test_Config(TestCase):

    config = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.config  = Config()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.config.load_values()

    def test_load_values(self):
        config = self.config

        self.assertEqual(config.gw_sdk_address , os.environ.get("GW_SDK_ADDRESS" , DEFAULT_GW_SDK_ADDRESS))
        self.assertEqual(config.gw_sdk_port    , int(os.environ.get("GW_SDK_PORT", DEFAULT_GW_SDK_PORT)))
        self.assertEqual(config.hd1_location   , os.environ.get("HD1_LOCATION"   , DEFAULT_HD1_LOCATION))
        self.assertEqual(config.hd2_location   , os.environ.get("HD2_LOCATION"   , DEFAULT_HD2_LOCATION))
        self.assertEqual(config.hd3_location   , os.environ.get("HD3_LOCATION"   , DEFAULT_HD3_LOCATION))
        self.assertEqual(config.root_folder    , os.environ.get("ROOT_FOLDER"    , DEFAULT_ROOT_FOLDER))
        self.assertEqual(config.endpoints      , json.loads(os.environ.get("ENDPOINTS"      , DEFAULT_ENDPOINTS)))
        assert config.endpoints['Endpoints'][0]['IP']
        assert config.endpoints['Endpoints'][0]['Port']

        assert folder_exists(config.root_folder         )
        assert folder_exists(config.hd1_location        )
        assert folder_exists(config.hd2_location        )
        assert folder_exists(config.hd2_data_location   )
        assert folder_exists(config.hd2_status_location )
        assert folder_exists(config.hd3_location        )

        # check config_cache
        config.root_folder = 'aaa'
        assert Config().root_folder == 'aaa'

        config.load_values()
        assert config  .root_folder == DEFAULT_ROOT_FOLDER
        assert Config().root_folder == DEFAULT_ROOT_FOLDER

    def test_ensure_last_char_is_not_forward_slash(self):
        assert self.config.ensure_last_char_is_not_forward_slash(''     ) == ''
        assert self.config.ensure_last_char_is_not_forward_slash('\\'   ) == ''
        assert self.config.ensure_last_char_is_not_forward_slash('/'    ) == ''
        assert self.config.ensure_last_char_is_not_forward_slash('/a'   ) == '/a'
        assert self.config.ensure_last_char_is_not_forward_slash('./a'  ) == './a'
        assert self.config.ensure_last_char_is_not_forward_slash('./a/' ) == './a'
        assert self.config.ensure_last_char_is_not_forward_slash('/a/b' ) == '/a/b'
        assert self.config.ensure_last_char_is_not_forward_slash('/a/b/') == '/a/b'

    def test_get_values(self):
        values = self.config.values()
        assert self.config.values().get('root_folder') == self.config.root_folder
        assert list_set(values) == ['elastic_host', 'elastic_port', 'elastic_schema', 'endpoints', 'hd1_location', 'hd2_data_location', 'hd2_location', 'hd2_status_location', 'hd3_location', 'kibana_host', 'kibana_port', 'root_folder', 'thread_count']

    def test_set_root_folder(self):
        root_folder = temp_folder()
        assert self.config.root_folder != root_folder
        self.config.set_root_folder(root_folder)
        assert self.config.root_folder  == root_folder

        assert self.config.hd1_location == path_combine(root_folder, DEFAULT_HD1_NAME)
        assert self.config.hd2_location == path_combine(root_folder, DEFAULT_HD2_NAME)
        assert self.config.hd3_location == path_combine(root_folder, DEFAULT_HD3_NAME)

        assert folder_exists(self.config.root_folder        )
        assert folder_exists(self.config.hd1_location       )
        assert folder_exists(self.config.hd2_location       )
        assert folder_exists(self.config.hd2_data_location  )
        assert folder_exists(self.config.hd2_status_location)
        assert folder_exists(self.config.hd3_location       )

        folder_delete_all(root_folder)

        assert folder_not_exists(self.config.root_folder)
        assert folder_not_exists(self.config.hd1_location)
        assert folder_not_exists(self.config.hd2_location)
        assert folder_not_exists(self.config.hd3_location)



    def test_set_hd1_location(self):
        hd1_location = path_combine(temp_folder(), 'aaaa')
        assert file_not_exists(hd1_location)
        self.config.set_hd1_location(hd1_location)
        assert self.config.hd1_location == hd1_location
        assert file_exists(hd1_location)
        self.config.load_values()
        assert self.config.hd1_location == './test_data/scenario-1/hd1'
        assert folder_delete_all(hd1_location)

    def test_set_hd2_location(self):
        hd2_location = path_combine(temp_folder(), 'bbb')
        assert file_not_exists(hd2_location)
        self.config.set_hd2_location(hd2_location)
        assert self.config.hd2_location         == hd2_location
        assert self.config.hd2_data_location    == path_combine(hd2_location, DEFAULT_HD2_DATA_NAME  )
        assert self.config.hd2_status_location  == path_combine(hd2_location, DEFAULT_HD2_STATUS_NAME)
        assert file_exists(hd2_location)

        self.config.load_values()
        assert self.config.hd2_location == './test_data/scenario-1/hd2'
        assert folder_delete_all(hd2_location)

    def test_set_hd3_location(self):
        hd3_location = path_combine(temp_folder(), 'cccc')
        assert file_not_exists(hd3_location)
        self.config.set_hd3_location(hd3_location)
        assert self.config.hd3_location == hd3_location
        assert file_exists(hd3_location)
        self.config.load_values()
        assert self.config.hd3_location == './test_data/scenario-1/hd3'
        assert folder_delete_all(hd3_location)