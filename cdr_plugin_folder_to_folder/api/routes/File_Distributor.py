from cdr_plugin_folder_to_folder.file_distribution.File_Distributor import File_Distributor
from fastapi import APIRouter

router_params = { "prefix": "/file-distributor"  ,
                  "tags"  : ['File Distributor'] }
router        = APIRouter(**router_params)

@router.get("/hd1/{num_of_files}")
def get_hd1_files(num_of_files: int):
    list=File_Distributor().get_hd1_files(num_of_files=num_of_files)
    return list

@router.get("/hd2/metadata/{num_of_files}")
def get_hd2_metadata_files(num_of_files: int):
    list=File_Distributor().get_hd2_metadata_files(num_of_files=num_of_files)
    return list

@router.get("/hd2/source/{num_of_files}")
def get_hd2_source_files(num_of_files: int):
    list=File_Distributor().get_hd2_source_files(num_of_files=num_of_files)
    return list

@router.get("/hd2/report/{num_of_files}")
def get_hd2_report_files(num_of_files: int):
    list=File_Distributor().get_hd2_report_files(num_of_files=num_of_files)
    return list

@router.get("/hd2/hash_folder_list/{num_of_files}")
def get_hd2_hash_folders_files(num_of_files : int):
    list=File_Distributor().get_hd2_hash_folder_list(num_of_files=num_of_files)
    return list

@router.get("/hd2/status")
def get_hd2_status_files():
    list=File_Distributor().get_hd2_status_hash_file()
    return list

@router.get("/hd3/{num_of_files}")
def get_hd3_files(num_of_files: int):
    list=File_Distributor().get_hd3_files(num_of_files=num_of_files)
    return list
