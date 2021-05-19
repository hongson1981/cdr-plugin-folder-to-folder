import os
import threading
import psutil
import logging as logger
from time import sleep

from prometheus_client import start_http_server, Gauge

# from osbot_utils.utils.Files                        import path_combine, folder_create, file_create
# from osbot_utils.utils.Json                         import json_save_file_pretty, json_load_file, file_exists
# from cdr_plugin_folder_to_folder.storage.Storage    import Storage
# from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
# from cdr_plugin_folder_to_folder.utils.PS_Utils import PS_Utils

from cdr_plugin_folder_to_folder.common_settings.Config import Config

logger.basicConfig(level=logger.INFO)

class MetricNames:
    GC_OBJECTS_COLLECTED       = 'python_gc_objects_collected_total'
    GC_OBJECTS_UNCOLLECTABLE   = 'python_gc_objects_uncollectable_total'
    GC_COLLECTIONS             = 'python_gc_collections_total'
    PROCESS_VIRUAL_MEMORY      = 'process_virtual_memory_bytes'
    PROCESS_RESIDENT_MEMORY    = 'process_resident_memory_bytes'
    PROCESS_START_TIME         = 'process_start_time_seconds'
    PROCESS_CPU_SECONDS        = 'process_cpu_seconds_total'
    PROCESS_OPEN_FDS           = 'process_open_fds'
    PROCESS_MAX_FDS            = 'process_max_fds'

    STATUS_HD1_FILES_COUNT     = 'status_hd1_files_count'

class Prometheus_Metrics:

    _instance = None
    def __new__(cls):                                               # singleton pattern
        if cls._instance is None:
            cls._instance = super(Prometheus_Metrics, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'instantiated') is False:                     # only set these values first time around
            self.instantiated   = True
            self.config = Config()
            start_http_server(self.config.prometheus_port)
            self.status_files_count = Gauge(MetricNames.STATUS_HD1_FILES_COUNT,'Total number of files on HD1')
            self.set_status_files_count(0)

    @classmethod
    def clear_instance(cls):
        del cls.instance

    def get_metric_from_text(self, text, metric_name):
        metric_name_position = text.find(f'\n{metric_name}') + 1
        if metric_name_position < 0: # not found
            return None
        metric_position = metric_name_position + len(metric_name)
        end_of_line_position = text.find('\n', metric_position)
        return text[metric_position:end_of_line_position].strip()

    def set_status_files_count(self, count):
        self.status_files_count.set(count)


