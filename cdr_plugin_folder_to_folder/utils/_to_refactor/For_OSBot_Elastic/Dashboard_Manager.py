from osbot_utils.utils.Files import file_create, path_combine
from osbot_utils.utils.Http import GET

import os
import time
from cdr_plugin_folder_to_folder.utils._to_refactor.For_OSBot_Elastic.Dashboard import Dashboard
from cdr_plugin_folder_to_folder.utils._to_refactor.For_OSBot_Elastic.Kibana import Kibana

KIBANA_TIMEOUT = 10

class Dashboard_Manager:

    def __init__(self, kibana):
        self.kibana         = kibana
        self.object_type    = 'dashboard_manager'
        pass

    def isDashbooard(self, filepath):
        if not os.path.exists(filepath):
            return False
        if not os.path.isfile(filepath):
            return False
        filename = os.path.basename(filepath)
        if not filename.endswith(".ndjson"):
            return False
        # TODO: more verifiations on the file content
        return True

    def import_dashboards(self, directory):
        if not os.path.exists(directory):
            return -1

        if not os.path.isdir(directory):
            return -1

        count = 0

        for i in range(0, KIBANA_TIMEOUT):
            if i == KIBANA_TIMEOUT:
                return count
            if self.kibana.enabled:
                break
            time.sleep(6) # 6 seconds delay

        for key in os.listdir(directory):
            filepath = path_combine(directory, key)
            if not self.isDashbooard(filepath):
                continue
            try:
                dashboard = Dashboard(kibana=self.kibana)
                dashboard.import_dashboard(filepath)
                count += 1
            except:
                pass

        return count