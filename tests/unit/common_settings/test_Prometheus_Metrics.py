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
        self.prometheus_url = f'http://{self.config.prometheus_host}:{self.config.prometheus_port}'

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def get_number(self, s):
        number = None
        try:
            number = float(s)
        except:
            return None
        return number

    def get_data(self):
        return requests.get(self.prometheus_url).text

    def test_set_status_files_count(self):
        self.metrics.set_status_files_count(0)
        data = self.get_data()
        assert data
        hd1_files_count = self.metrics.get_metric_from_text(data, MetricNames.HD1_FILES_COUNT)
        assert hd1_files_count
        assert self.is_number(hd1_files_count)
        assert 0 == self.get_number(hd1_files_count)

        self.metrics.set_status_files_count(10)
        data = self.get_data()
        assert data
        hd1_files_count = self.metrics.get_metric_from_text(data, MetricNames.HD1_FILES_COUNT)
        assert hd1_files_count
        assert self.is_number(hd1_files_count)
        assert 10 == self.get_number(hd1_files_count)