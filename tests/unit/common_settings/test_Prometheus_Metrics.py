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
        self.numeric_values = [0, 1, 2, 3, 10, 1.81, 81.54]

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

    def get_metric_from_text(self, text, metric_name, generation = None):
        if not generation is None:
            metric_name = metric_name + '{generation=' + f'"{generation}"' + '}'
        metric_name_position = text.find(f'\n{metric_name}') + 1
        if metric_name_position < 0: # not found
            return None
        metric_position = metric_name_position + len(metric_name)
        end_of_line_position = text.find('\n', metric_position)
        return text[metric_position:end_of_line_position].strip()

    def get_metric(self, metric_name, generation = None):
        data = self.get_data()
        if not data:
            return None
        return self.get_metric_from_text(data, metric_name, generation)

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

    # def test_set_status_current_status(self):

    def numeric_metric_set_get_test(self, method, metric_name):
        for value in self.numeric_values:
            method(value)
            metric = self.get_metric(metric_name)
            assert metric
            assert self.is_number(metric)
            assert value == self.get_number(metric)        

    def test_set_status_files_count(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_files_count, MetricNames.STATUS_FILES_COUNT)

    def test_set_status_files_copied(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_files_copied, MetricNames.STATUS_FILES_COPIED)

    def test_set_status_files_to_be_copied(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_files_to_be_copied, MetricNames.STATUS_FILES_TO_BE_COPIED)

    def test_set_status_files_to_process(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_files_to_process, MetricNames.STATUS_FILES_TO_PROCESS)

    def test_set_status_files_left_to_process(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_files_left_to_process, MetricNames.STATUS_FILES_LEFT_TO_PROCESS)

    def test_set_status_completed(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_completed, MetricNames.STATUS_COMPLETED)

    def test_set_status_not_supported(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_not_supported, MetricNames.STATUS_NOT_SUPPORTED)

    def test_set_status_failed(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_failed, MetricNames.STATUS_FAILED)

    def test_set_status_in_progress(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_in_progress, MetricNames.STATUS_IN_PROGRESS)

    def test_set_status_number_of_cpus(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_number_of_cpus, MetricNames.STATUS_NUMBER_OF_CPUS)

    # def test_set_status_cpu_utilization(self):
    #     self.numeric_metric_set_get_test(self.metrics.set_status_, MetricNames.STATUS_)

    def test_set_status_ram_utilization(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_ram_utilization, MetricNames.STATUS_RAM_UTILIZATION)

    def test_set_status_num_of_processes(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_num_of_processes, MetricNames.STATUS_NUM_OF_PROCESSES)

    def test_set_status_num_of_threads(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_num_of_threads, MetricNames.STATUS_NUM_OF_THREADS)

    def test_set_status_network_connections(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_network_connections, MetricNames.STATUS_NETWORK_CONNECTIONS)

    def test_set_status_disk_partitions(self):
        self.numeric_metric_set_get_test(self.metrics.set_status_disk_partitions, MetricNames.STATUS_DISK_PARTITIONS)


