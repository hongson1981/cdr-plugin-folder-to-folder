import os
import os.path
import shutil
import base64

# todo: remove methods that are provided by osbot_utils
class FileService:

    @staticmethod
    def copy_file(src,dst):
        try:
            shutil.copyfile(src, dst)
        except Exception as error:
            raise error

    @staticmethod
    def copy_folder(src,dest):
        try:
            shutil.copytree(src, dest)
        except Exception as error:
            raise error

    @staticmethod
    def move_file(src,dst):
        try:
            shutil.move(src, dst)
        except Exception as error:
            raise error

    @staticmethod
    def wrtie_file(folder,file_name,content):
        try:
            text_file_name = os.path.join(folder, file_name)
            with open(text_file_name, "w") as fp:
                fp.write(str(content))
                fp.close()
        except Exception as error:
            raise error

    @staticmethod
    def wrtie_binary_file(folder,file_name,content):
        try:
            binary_file_name = os.path.join(folder, file_name)
            with open(binary_file_name, "wb") as fp:
                fp.write(content)
                fp.close()
        except Exception as error:
            raise error

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

