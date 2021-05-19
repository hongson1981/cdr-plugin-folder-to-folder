from os import environ
from unittest import TestCase
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import is_number, list_set

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.common_settings.Prometheus_Metrics import Prometheus_Metrics, MetricNames
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

import requests

class test_Prometheus_Metrics(TestCase):

    def setUp(self) -> None:
        self.config = Config()
        self.metrics = Prometheus_Metrics()

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def test_prometheus_data(self):
        prometheus_url = f'http://{self.config.prometheus_host}:{self.config.prometheus_port}'
        prometheus_data = requests.get(prometheus_url).text
        assert prometheus_data
        hd1_files_count = self.metrics.get_metric_from_text(prometheus_data, MetricNames.HD1_FILES_COUNT)
        assert hd1_files_count
        assert self.is_number(hd1_files_count)
