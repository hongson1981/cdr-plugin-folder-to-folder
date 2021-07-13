import json
import os
import shutil

# todo: to delete (check if this is stil used)
class File_Service:

    def wrtie_json_file(self,folder,file_name,content):
        try:
            self.metadata_file_name = os.path.join(folder, file_name)
            with open(self.metadata_file_name, 'w') as json_file:
                json.dump(content, json_file)
        except Exception as error:
            raise error

    def read_json_file(self,file_path):
        try:
            f = open(file_path, "r")
            content = json.loads(f.read())
            return content
        except Exception as error:
            raise error



