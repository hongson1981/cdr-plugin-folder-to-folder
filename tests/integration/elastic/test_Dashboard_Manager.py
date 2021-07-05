from unittest import TestCase

import os
import pytest
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_create, file_contents, path_combine
from osbot_utils.utils.Http import GET
from osbot_utils.utils.Misc import list_set, random_text

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils._to_refactor.For_OSBot_Elastic.Dashboard_Manager import Dashboard_Manager
from cdr_plugin_folder_to_folder.utils._to_refactor.For_OSBot_Elastic.Kibana import Kibana

#@pytest.mark.skip
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing


class test_Dashboard(TestCase):

    def setUp(self) -> None:
        self.config = Config()
        Setup_Testing().configure_config(self.config)
        self.host   = self.config.kibana_host
        self.port   = self.config.kibana_port
        self.kibana = Kibana(host=self.host, port=self.port).setup()

        if self.kibana.enabled is False:
            pytest.skip('Elastic server not available')

        self.dashboard_manager  = Dashboard_Manager(kibana=self.kibana)

    def get_project_root(self):
        current_directory = os.getcwd();
        root = "/"

        while True:
            list_ = os.listdir(current_directory)
            parent_directory = os.path.dirname(current_directory)
            if current_directory in (root, parent_directory):
                break
            if ".env.sample" in list_:
                return current_directory
            current_directory = parent_directory

    def get_kibana_dashboards_dir(self):
        project_root = self.get_project_root()
        test_data_dir = path_combine(project_root, "test_data")
        return path_combine(test_data_dir, "kibana-dashboards")

    def test_import_all_dashboards(self):
        kibana_dashboards_dir = self.get_kibana_dashboards_dir()
        assert os.path.exists(kibana_dashboards_dir)
        assert os.path.isdir(kibana_dashboards_dir)
        count = self.dashboard_manager.import_dashboards(kibana_dashboards_dir)
        assert count == 7