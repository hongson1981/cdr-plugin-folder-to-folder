from unittest import TestCase
from unittest.mock import patch, call

import os
import pytest

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json import json_load_file

from cdr_plugin_folder_to_folder.processing.Analysis_Elastic import Analysis_Elastic
from cdr_plugin_folder_to_folder.utils.testing.Setup_Testing import Setup_Testing

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
    )

class test_Analysis_Elastic(TestCase):
    test_file = None
    @classmethod
    def setUpClass(cls) -> None:
        cls.file_hash            = '458d2ceb57b1bac2866c43e16cc9392b017aa48f0689876df25399d0f7ad198c'

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self) -> None:

        analysis_file_path = os.path.join(FIXTURE_DIR, 'analysis.json')
        assert os.path.isfile(analysis_file_path)

        self.analysis_data = json_load_file(analysis_file_path)
        assert self.analysis_data is not None
        assert len(self.analysis_data ) == 6

        self.original_hash   = self.analysis_data[self.file_hash]['original_hash']
        assert self.original_hash == self.file_hash

        self.analysis_elastic = Analysis_Elastic()
        self.analysis_elastic.setup()

        if self.analysis_elastic.enabled is False:
            pytest.skip('Elastic server not available')


    def test_add_analysis(self):

        analysis_add_report = self.analysis_elastic.add_analysis(self.analysis_data)

        assert analysis_add_report.get('_shards').get('successful') == 1

        assert self.analysis_elastic.get_analysis   (original_hash=self.original_hash)               == self.analysis_data[self.file_hash]
        assert self.analysis_elastic.delete_analysis(original_hash=self.original_hash).get('result') == 'deleted'
        assert self.analysis_elastic.get_analysis   (original_hash=self.original_hash)               == {}

    def test_clear_all_report(self):
        self.analysis_elastic.delete_all_analysis()
        assert len(self.analysis_elastic.get_all_analysis()) == 0