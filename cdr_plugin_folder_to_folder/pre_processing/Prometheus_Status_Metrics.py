# import os
# import threading
# import psutil
import logging as logger
from time import sleep

from prometheus_client import Gauge, Enum
from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.pre_processing.Processing_Status import Processing_Status, Processing_Status_States
from cdr_plugin_folder_to_folder.common_settings.Prometheus_Metrics_Page import Prometheus_Metrics_Page

logger.basicConfig(level=logger.INFO)

class MetricNames:
    # generic metric names
    GC_OBJECTS_COLLECTED       = 'python_gc_objects_collected_total'
    GC_OBJECTS_UNCOLLECTABLE   = 'python_gc_objects_uncollectable_total'
    GC_COLLECTIONS             = 'python_gc_collections_total'
    PROCESS_VIRUAL_MEMORY      = 'process_virtual_memory_bytes'
    PROCESS_RESIDENT_MEMORY    = 'process_resident_memory_bytes'
    PROCESS_START_TIME         = 'process_start_time_seconds'
    PROCESS_CPU_SECONDS        = 'process_cpu_seconds_total'
    PROCESS_OPEN_FDS           = 'process_open_fds'
    PROCESS_MAX_FDS            = 'process_max_fds'

    # Status class metric names
    STATUS_CURRENT_STATUS         = 'status_current_status'
    STATUS_FILES_COUNT            = 'status_hd1_files_count'
    STATUS_FILES_COPIED           = 'status_files_copied'
    STATUS_FILES_TO_BE_COPIED     = 'status_files_to_be_copied'
    STATUS_FILES_TO_PROCESS       = 'status_files_to_process'
    STATUS_FILES_LEFT_TO_PROCESS  = 'status_files_left_to_process'
    STATUS_COMPLETED              = 'status_completed'
    STATUS_NOT_SUPPORTED          = 'status_not_supported'
    STATUS_FAILED                 = 'status_failed'
    STATUS_IN_PROGRESS            = 'status_in_progress'
    STATUS_NUMBER_OF_CPUS         = 'status_number_of_cpus'
    STATUS_CPU_UTILIZATION        = 'status_cpu_utilization'
    STATUS_RAM_UTILIZATION        = 'status_ram_utilization'
    STATUS_NUM_OF_PROCESSES       = 'status_num_of_processes'
    STATUS_NUM_OF_THREADS         = 'status_num_of_threads'
    STATUS_NETWORK_CONNECTIONS    = 'status_network_connections'
    STATUS_DISK_PARTITIONS        = 'status_disk_partitions'

class Prometheus_Status_Metrics:

    _instance = None
    def __new__(cls):                                               # singleton pattern
        if cls._instance is None:
            cls._instance = super(Prometheus_Status_Metrics, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'instantiated') is False:                     # only set these values first time around
            self.instantiated = True
            self.config = Config()
            self.metrics_page = Prometheus_Metrics_Page()

            self.status_current_status = Enum ( MetricNames.STATUS_CURRENT_STATUS,
                                                'The Current processing state',
                                                states = Processing_Status_States
                                              )
            self.status_files_count             = Gauge(MetricNames.STATUS_FILES_COUNT,             'Total number of files on HD1')
            self.status_files_copied            = Gauge(MetricNames.STATUS_FILES_COPIED,            'Files copied to HD2')
            self.status_files_to_be_copied      = Gauge(MetricNames.STATUS_FILES_TO_BE_COPIED,      'Files left to be copied to HD2')
            self.status_files_to_process        = Gauge(MetricNames.STATUS_FILES_TO_PROCESS,        'Files to be processed on HD2')
            self.status_files_left_to_process   = Gauge(MetricNames.STATUS_FILES_LEFT_TO_PROCESS,   'Files still not processed on HD2')
            self.status_completed               = Gauge(MetricNames.STATUS_COMPLETED,               'Files processed successfully')
            self.status_not_supported           = Gauge(MetricNames.STATUS_NOT_SUPPORTED,           'Files not currently supported')
            self.status_failed                  = Gauge(MetricNames.STATUS_FAILED,                  'Files whose processing completed with errors')
            self.status_in_progress             = Gauge(MetricNames.STATUS_IN_PROGRESS,             'Files whose processing in not completed yet')
            self.status_number_of_cpus          = Gauge(MetricNames.STATUS_NUMBER_OF_CPUS,          'Number of CPUs on the system')
            #self.status_cpu_utilization         = Gauge(MetricNames.STATUS_CPU_UTILIZATION,'')
            self.status_ram_utilization         = Gauge(MetricNames.STATUS_RAM_UTILIZATION,         'Current RAM utilization')
            self.status_num_of_processes        = Gauge(MetricNames.STATUS_NUM_OF_PROCESSES,        'Current number of processes on the system')
            self.status_num_of_threads          = Gauge(MetricNames.STATUS_NUM_OF_THREADS,          'Current number of threads on the system')
            self.status_network_connections     = Gauge(MetricNames.STATUS_NETWORK_CONNECTIONS,     'Current number of network connections on the system')
            self.status_disk_partitions         = Gauge(MetricNames.STATUS_DISK_PARTITIONS,         'Number of disk partitions on the system')

            self.set_status_current_status(Processing_Status.NONE)
            self.set_status_files_count(0)
            self.set_status_files_copied(0)
            self.set_status_files_to_be_copied(0)
            self.set_status_files_to_process(0)
            self.set_status_files_left_to_process(0)
            self.set_status_completed(0)
            self.set_status_not_supported(0)
            self.set_status_failed(0)
            self.set_status_in_progress(0)
            self.set_status_number_of_cpus(0)
            #self.set_status_cpu_utilization(0)
            self.set_status_ram_utilization(0)
            self.set_status_num_of_processes(0)
            self.set_status_num_of_threads(0)
            self.set_status_network_connections(0)
            self.set_status_disk_partitions(0)

    @classmethod
    def clear_instance(cls):
        del cls.instance

    def set_gauge(self, gauge, value):
        if value is None:
            gauge.set(0)
        else:
            gauge.set(value)

    # Status class metrics

    def set_status_files_count(self, count):
        self.set_gauge(self.status_files_count, count)

    def set_status_current_status(self, status):
        if not status in Processing_Status_States:
           return

        self.status_current_status.state(status)

    def set_status_files_copied(self, count):
       self.set_gauge(self.status_files_copied, count)

    def set_status_files_to_be_copied(self, count):
       self.set_gauge(self.status_files_to_be_copied, count)

    def set_status_files_to_process(self, count):
       self.set_gauge(self.status_files_to_process, count)

    def set_status_files_left_to_process(self, count):
       self.set_gauge(self.status_files_left_to_process, count)

    def set_status_completed(self, count):
       self.set_gauge(self.status_completed, count)

    def set_status_not_supported(self, count):
       self.set_gauge(self.status_not_supported, count)

    def set_status_failed(self, count):
       self.set_gauge(self.status_failed, count)

    def set_status_in_progress(self, count):
       self.set_gauge(self.status_in_progress, count)

    def set_status_number_of_cpus(self, count):
       self.set_gauge(self.status_number_of_cpus, count)

    # def set_status_cpu_utilization(self, count):
    #    self.set_gauge(self.status_cpu_utilization, count)

    def set_status_ram_utilization(self, count):
       self.set_gauge(self.status_ram_utilization, count)

    def set_status_num_of_processes(self, count):
       self.set_gauge(self.status_num_of_processes, count)

    def set_status_num_of_threads(self, count):
       self.set_gauge(self.status_num_of_threads, count)

    def set_status_network_connections(self, count):
       self.set_gauge(self.status_network_connections, count)

    def set_status_disk_partitions(self, count):
       self.set_gauge(self.status_disk_partitions, count)


