from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils.testing.Direct_API_Server import Direct_API_Server


class test_Health(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Direct_API_Server().setup()

    def test_root(self):
        assert self.client.GET("/") == {'status': 'ok'}

    def test_health(self):
        assert self.client.GET("/health") == {'status': 'ok'}

    def test_status(self):
        pprint(self.client.GET("/status"))

    def test_version(self):
        assert self.client.GET("/version") == { "version": Config().api_version }
