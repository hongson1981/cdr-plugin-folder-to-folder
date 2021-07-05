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
        import_result = dashboard.import_dashboard_from_github(dashboard_file_name='processed-files-v8.ndjson')
        assert import_result == '{"successCount":8,"success":true,"warnings":[],"successResults":[{"type":"index-pattern","id":"8ec83df0-9fca-11eb-977f-33534b5f4ee3","meta":{"title":"files_metadata","icon":"indexPatternApp"},"overwrite":true},{"type":"index-pattern","id":"1f81c950-ab43-11eb-9a88-73c5560283fb","meta":{"title":"files_metadata","icon":"indexPatternApp"},"overwrite":true},{"type":"lens","id":"a6714260-a08f-11eb-977f-33534b5f4ee3","meta":{"title":"Rebuild status","icon":"lensApp"},"overwrite":true},{"type":"lens","id":"72b93700-a5fa-11eb-b908-5f3bf6b29bb1","meta":{"title":"files_metadata - count files","icon":"lensApp"},"overwrite":true},{"type":"lens","id":"472f47a0-a5fa-11eb-b908-5f3bf6b29bb1","meta":{"title":"Files Metadata - Sum File size","icon":"lensApp"},"overwrite":true},{"type":"index-pattern","id":"4d3408b0-aa0b-11eb-9af3-352b8da8b63c","meta":{"title":"files_metadata","icon":"indexPatternApp"},"overwrite":true},{"type":"search","id":"4aff02f0-ab4d-11eb-9a88-73c5560283fb","meta":{"title":"discover-files-metadata","icon":"discoverApp"},"overwrite":true},{"type":"dashboard","id":"d73d7220-ab6f-11eb-b1b2-a1d32a234c46","meta":{"title":"Processed Files v8","icon":"dashboardApp"},"overwrite":true}]}'

    def test_export_dashboard(self):
        dashboard_id = 'd73d7220-ab6f-11eb-b1b2-a1d32a234c46'
        dashboard = Dashboard(kibana=self.kibana, dashboard_id=dashboard_id)
        export_data = dashboard.export_dashboard()
        assert dashboard_id in export_data

    def test_export_not_existing_dashboard(self):
        dashboard_id = 'ffdd80b7-11eb-4dd9-b8ce-293254a5c961'
        dashboard = Dashboard(kibana=self.kibana, dashboard_id=dashboard_id)
        export_data = dashboard.export_dashboard()
        assert export_data == '{"statusCode":400,"error":"Bad Request","message":"Error fetching objects to export","attributes":{"objects":[{"id":"ffdd80b7-11eb-4dd9-b8ce-293254a5c961","type":"dashboard","error":{"statusCode":404,"error":"Not Found","message":"Saved object [dashboard/ffdd80b7-11eb-4dd9-b8ce-293254a5c961] not found"}}]}}'
