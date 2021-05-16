import platform
import sys
from unittest import TestCase
from unittest.mock import patch

import psutil
from osbot_utils.utils.Dev import pprint

from cdr_plugin_folder_to_folder.utils.PS_Utils import PS_Utils


class test_PS_Utils(TestCase):

    def setUp(self) -> None:
        self.ps_utils = PS_Utils()

    def test_cpu_count(self):
        assert self.ps_utils.cpu_count() == psutil.cpu_count()
        with patch.object(psutil, 'cpu_count', return_value=111       ): assert self.ps_utils.cpu_count() == 111
        with patch.object(psutil, 'cpu_count', side_effect=Exception()): assert self.ps_utils.cpu_count() == -1

    def test_cpu_percent(self):
        kwargs = {"interval":0.001 }
        assert type(self.ps_utils.cpu_percent(**kwargs)) is float
        with patch.object(psutil, 'cpu_percent', return_value=111       ): assert self.ps_utils.cpu_percent() == 111
        with patch.object(psutil, 'cpu_percent', side_effect=Exception()): assert self.ps_utils.cpu_percent() == -1

    def test_disk_partitions_count(self):
        assert self.ps_utils.disk_partitions_count() == len(psutil.disk_partitions())
        with patch.object(psutil, 'disk_partitions', return_value=['a']     ): assert self.ps_utils.disk_partitions_count() == 1
        with patch.object(psutil, 'disk_partitions', side_effect=Exception()): assert self.ps_utils.disk_partitions_count() == -1

    def test_net_connections_count(self):
        kind = 'tcp'
        if platform.system() == "Darwin":                               # psutil.net_connections needs admin rights in OSX
            assert self.ps_utils.net_connections_count(kind=kind) == -1
        else:
            assert self.ps_utils.net_connections_count(kind=kind) == len(psutil.net_connections(kind=kind))
        with patch.object(psutil, 'net_connections', return_value=[0,1]      ): assert self.ps_utils.net_connections_count() == 2
        with patch.object(psutil, 'net_connections', side_effect=Exception()): assert self.ps_utils.net_connections_count() == -1

    def test_processes_count(self):
        assert self.ps_utils.processes_count() == len(psutil.pids())
        with patch.object(psutil, 'pids', return_value=[1,2,3,4 ]): assert self.ps_utils.processes_count() == 4
        with patch.object(psutil, 'pids', side_effect=Exception()): assert self.ps_utils.processes_count() == -1

    def test_threads_count(self):
        assert self.ps_utils.threads_count() > len(psutil.pids())
        with patch.object(psutil, 'pids', side_effect=Exception()): assert self.ps_utils.threads_count() == -1

    def test_virtual_memory_percent(self):
        assert self.ps_utils.virtual_memory_percent() == psutil.virtual_memory().percent
        with patch.object(psutil, 'virtual_memory', side_effect=Exception()): assert self.ps_utils.virtual_memory_percent() == -1