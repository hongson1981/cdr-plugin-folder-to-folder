from osbot_utils.decorators.methods.cache_on_self  import cache_on_self

from cdr_plugin_folder_to_folder.pre_processing.Hash_Json import Hash_Json
from cdr_plugin_folder_to_folder.storage.Storage import Storage
from cdr_plugin_folder_to_folder.utils.Elastic     import Elastic
from cdr_plugin_folder_to_folder.utils.Log_Duration import log_duration
from cdr_plugin_folder_to_folder.utils.Logging import log_debug
from cdr_plugin_folder_to_folder.utils._to_refactor.For_OSBot_Elastic.Kibana import Kibana

DEFAULT_TIME_FIELD = 'timestamp'

class Metadata_Elastic:
    def __init__(self):
        self.index_name = 'files_metadata'
        self.id_key     = 'original_hash'
        self.time_field = DEFAULT_TIME_FIELD
        self.enabled    = False
        self.storage    = Storage()

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

    def add_metadata(self, metadata):
        return self.elastic().add(metadata)

    def delete_metadata(self,original_hash):
        return self.elastic().delete(record_id=original_hash)

    @log_duration
    def delete_all_metadata(self):
        #log_debug(message=f"Deleting all data and recreating {self.index_name} index and index pattern")
        return self.setup(delete_existing=True)

    def get_all_metadata(self):
        return self.elastic().search_using_lucene('*')

    def get_metadata(self, original_hash):
        return self.elastic().get_data(record_id=original_hash)

    @log_duration
    def reload_metadatas(self):
        hash_json = Hash_Json().reset()
        hash_data = hash_json.data()
        metadatas = self.storage.hd2_metadatas()
        count     = len(metadatas)
        log_debug(message=f"Reloading {count} currently in hd2/data")
        for metadata in metadatas:
            self.add_metadata(metadata)
            file_hash   = metadata.get('original_hash')
            file_name   = metadata.get('file_name')
            file_status = metadata.get('rebuild_status')
            hash_data[file_hash] = {"file_name"  : file_name    ,       # todo: refactor this so that it is not done here
                                    "file_status": file_status  }       #       (which happened due to the performance hit of the current Hash_Json file)
                                                                        #       when using:
                                                                        #         hash_json.add_file(file_hash=file_hash, file_name=file_name)
                                                                        #         hash_json.update_status(index=file_hash, updated_status=file_status)
        hash_json.save()
        return count

    @log_duration
    def reload_hash_json(self):
        hash_json = Hash_Json().reset()
        hash_data = hash_json.data()
        metadatas = self.storage.hd2_metadatas()
        for metadata in metadatas:
            file_hash = metadata.get('original_hash')
            file_name = metadata.get('file_name')
            file_status = metadata.get('rebuild_status')
            hash_data[file_hash] = {"file_name": file_name,  # todo: refactor this so that it is not done here
                                    "file_status": file_status}  # (which happened due to the performance hit of the current Hash_Json file)
        hash_json.save()
        return f'Hash_Json reloaded for {len(metadatas)} metadata items'

    def reload_elastic_data(self):
        self.delete_all_metadata()
        count = self.reload_metadatas()

        return f'Elastic {self.index_name} has been reset and {count} metadata items reloaded'

    def reload_kibana_dashboards(self):
        kibana = self.elastic().kibana()
        dashboard_file_names = ['processed-files-v8.ndjson', 'File-Analysis-Threat-Level-v2.ndjson', 'errors-and-duration.ndjson' ]
        result = []
        for dashboard_file_name in dashboard_file_names:
            result.append(kibana.dashboard_import_from_github(dashboard_file_name=dashboard_file_name))
        return f"reloaded {len(result)} dashboards"


