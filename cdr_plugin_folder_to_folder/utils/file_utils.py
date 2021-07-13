import os
import os.path
import shutil
import base64

# todo: remove methods that are provided by osbot_utils
class FileService:

    @staticmethod
    def files_in_folder(folder_path):
        files = []
        for folderName, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                files.append(os.path.join(folderName, filename))
        return files

    @staticmethod
    def base64encode(file_path):
        try:
            with open(file_path, "rb") as bin_file:
                encoded_bytes = base64.b64encode(bin_file.read())
                encoded_string = encoded_bytes.decode('ascii')
                return encoded_string
        except Exception as error:
            return ""

    @staticmethod
    def base64decode(base64encoded):
        try:
            return base64.b64decode(base64encoded)
        except Exception as error:
            return ""

