from os import environ
from unittest import TestCase
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import list_set

from cdr_plugin_folder_to_folder.api.Server_Status import Server_Status
from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing


class test_Server_Status(TestCase):

    def setUp(self) -> None:
        self.status = Server_Status()
        #Setup_Testing().configure_static_logging()

        #self.status.config.kibana_host='127.0.0.1'
        #self.status.config.elastic_host = '127.0.0.1'

    def test_now(self):
        result = self.status.now()
        assert list_set(result) == ['check_logging', 'config', 'date']
        assert result.get('config') == Config().values()
        #pprint(result)

    def test_check_logging(self):
        assert self.status.check_logging() == { 'server_online': 'not implemented' }
        # if logging.elastic().enabled:
        #     assert logging.elastic().server_online() is True
        #     assert list_set(self.status.check_logging()) == ['logged_data', 'record_id', 'server_online']