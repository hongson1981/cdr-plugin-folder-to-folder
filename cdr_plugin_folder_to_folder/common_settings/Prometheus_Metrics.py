import os
import threading
import psutil
import logging as logger
from time import sleep

from prometheus_client import start_http_server

from osbot_utils.utils.Files                        import path_combine, folder_create, file_create
from osbot_utils.utils.Json                         import json_save_file_pretty, json_load_file, file_exists
from cdr_plugin_folder_to_folder.storage.Storage    import Storage
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.PS_Utils import PS_Utils

from cdr_plugin_folder_to_folder.common_settings.Config import Config

logger.basicConfig(level=logger.INFO)

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

    @classmethod
    def clear_instance(cls):
        del cls.instance


