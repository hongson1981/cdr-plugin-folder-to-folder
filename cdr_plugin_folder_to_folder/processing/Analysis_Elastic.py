from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from cdr_plugin_folder_to_folder.utils.Elastic import Elastic
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.Logging import log_debug

DEFAULT_TIME_FIELD = 'timestamp'

class Analysis_Elastic:
    def __init__(self):
        self.index_name = 'analysis_json'
        self.id_key     = 'original_hash'
        self.enabled    = False
        self.time_field = DEFAULT_TIME_FIELD
        self.storage = Storage()

    @cache_on_self
    def elastic(self):
        return Elastic(index_name=self.index_name, id_key=self.id_key, time_field=self.time_field)

    def setup(self, delete_existing=False):
        elastic = self.elastic()
        elastic.connect()
        elastic.setup()
        if elastic.enabled:
            elastic.create_index_and_index_pattern(delete_existing=delete_existing)
            self.enabled = True
        return self

    # class methods

    def add_analysis(self, analysis_report):
        return self.elastic().add(analysis_report)

    def delete_analysis(self,original_hash):
        return self.elastic().delete(record_id=original_hash)

    def delete_all_analysis(self):
        return self.setup(delete_existing=True)

    def get_all_analysis(self):
        return self.elastic().search_using_lucene('*')

    def get_analysis(self, original_hash):
        return self.elastic().get_data(record_id=original_hash)

    def clear_elastic_analysis(self):
        self.delete_all_analysis()
        return f'Elastic {self.index_name} has been reset'




