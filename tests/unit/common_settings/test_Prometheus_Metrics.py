from os import environ
from unittest import TestCase
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import is_number, list_set, none_or_empty

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.common_settings.Prometheus_Metrics import Prometheus_Metrics, MetricNames
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing
#from cdr_plugin_folder_to_folder.utils.testing.Test_Data import Test_Data

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

    def get_metric(self, metric_name, generation = None):
        data = self.get_data()
        if not data:
            return None
        return self.metrics.get_metric_from_text(data, metric_name, generation)

    def test_common_metrics(self):
        metric = self.get_metric(MetricNames.GC_OBJECTS_COLLECTED,0)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.GC_OBJECTS_UNCOLLECTABLE,0)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.GC_COLLECTIONS,0)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.PROCESS_VIRUAL_MEMORY)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.PROCESS_RESIDENT_MEMORY)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.PROCESS_CPU_SECONDS)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.PROCESS_START_TIME)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.PROCESS_OPEN_FDS)
        assert metric
        assert self.is_number(metric)

        metric = self.get_metric(MetricNames.PROCESS_MAX_FDS)
        assert metric
        assert self.is_number(metric)


    def test_set_status_files_count(self):
        values = [0, 1, 2, 3, 10]
        for value in values:
            self.metrics.set_status_files_count(value)
            hd1_files_count = self.get_metric(MetricNames.STATUS_HD1_FILES_COUNT)
            assert hd1_files_count
            assert self.is_number(hd1_files_count)
            assert value == self.get_number(hd1_files_count)

