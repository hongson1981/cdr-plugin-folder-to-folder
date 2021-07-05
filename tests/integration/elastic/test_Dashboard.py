from unittest import TestCase

import pytest
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_create, file_contents
from osbot_utils.utils.Http import GET
from osbot_utils.utils.Misc import list_set, random_text

from cdr_plugin_folder_to_folder.common_settings.Config import Config
from cdr_plugin_folder_to_folder.utils.Elastic import Elastic
from cdr_plugin_folder_to_folder.utils._to_refactor.For_OSBot_Elastic.Dashboard import Dashboard
from cdr_plugin_folder_to_folder.utils._to_refactor.For_OSBot_Elastic.Index_Pattern import Index_Pattern
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

        self.dashboard_name   = 'temp_dashbobard'
        self.dashboard  = Dashboard(kibana=self.kibana, dashboard_name=self.dashboard_name)

    def test_create_info_exists_delete(self):
        result = self.dashboard.create()
        pprint(result)
        return

        assert result.get('attributes').get('title') == self.pattern_name
        assert self.index_pattern.exists() is True
        assert list_set(self.index_pattern.info()) == ['fields', 'id', 'namespaces', 'references', 'score', 'title',
                                                       'type', 'updated_at']
        assert Index_Pattern(kibana=self.kibana, pattern_name=random_text()).info() == {}
        assert self.index_pattern.delete() is True

    def test_import_dashboard(self):
        dashboard = Dashboard(kibana=self.kibana)
        pprint(dashboard.import_dashboard_from_github(dashboard_file_name='processed-files-v8.ndjson'))
        pprint(dashboard.import_dashboard_from_github(dashboard_file_name='KD1.ndjson'))

    def test_export_dashboard(self):
        dashboard_id = 'd73d7220-ab6f-11eb-b1b2-a1d32a234c46'
        dashboard = Dashboard(kibana=self.kibana, dashboard_id=dashboard_id)
        export_data = dashboard.export_dashboard()
        pprint(file_create(contents=export_data))