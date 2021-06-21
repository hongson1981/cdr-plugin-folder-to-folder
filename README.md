# cdr-plugin-folder-to-folder

**Repo Workflows**

[![](https://github.com/filetrust/cdr-plugin-folder-to-folder/actions/workflows/run-tests.yml/badge.svg)](https://coveralls.io/github/filetrust/cdr-plugin-folder-to-folder)

## Project 

- This project aims to create a deployment that is able to process **1TB** of unique unsafe files, shared on the harddrive. 
- Implementation should pick up these files and process them via Rebuild engine in a deployment based on 2 ESXi servers.

## Arhitecture 

- Workflow cluster
- Worker cluster
- Load balancer
- Monitoring
- 3 Harddisks (source, evidence and target)

![cdr-plugin-folder-to-folder-architecture](https://user-images.githubusercontent.com/70108899/113837900-907a0c80-978e-11eb-8ad6-2fc862ee1821.png)


## Flow diagram

![image](https://user-images.githubusercontent.com/70108899/113400135-a314d000-93a1-11eb-8b5f-5d9fb3679264.png)

## Data mapping

![image](https://user-images.githubusercontent.com/70108899/113837649-57da3300-978e-11eb-8ac6-77ef13db2562.png)

## The Metadata module

The Metadata_Service class manages the creation and updating of the metadata.json files in the HASH directories on HD2

- `get_metadata` - takes the path of the file and creates the JSON object
- `get_from_file` - get the JSON object from the metadata.json file in the HASH directory
- `write_metadata_to_file` - saves the current JSON object to metadata.jsom file in the HASH directory
- `get_original_file_path` - obtains the original file path from metadata in the HASH directory
- `get_status` - gets current status stored in the metadate.json file of the HASH directory 
- `set_status` - updates the status stored in the metadate.json file of the HASH directory 

## PreProcessing Module Flow

![image](https://user-images.githubusercontent.com/70108899/113837363-0df14d00-978e-11eb-89f2-a7046e7b8ddb.png)

## Processing Module Flow

- Iterates through the HASH folders created during pre-processing on HD2
- For each HASH folder:
    - If the status in metadata is not "INITIAL" does nothing
    - Otherwise:
        - Updates the status in metadata to "IN PROGRESS"
        - Sends the file to be processed
        - Saves the processed file to the corresponding directory in HD3
        - Saves the processing report to the HASH folder
        - Updates the status to "COMPLETED"

- In `Loops Class`, `LoopHashDirectories` function iterates through HASH directories of HD2, for each of the directories, it initiated file processing with a call to `processDirectory` of the `File_Processing` class

- The `File_Processing class` is accessed with the `processDirectory` function. The function gets a HASH directory path on HD2 as a parameter and processes it.

![image](https://user-images.githubusercontent.com/70108899/113837515-38dba100-978e-11eb-9d82-8f6c32688ca5.png)

## Usage

- Set minio and jupyter notebook password 
    ```
     export ACCESS_TOKEN=
  
   ```
  
- Run `docker-compose up`

## Services

### Fast API

- Open `http://localhost:8880`
- Endpoints

| API Endpoint | Method | Description | 
|------|---------|---------    |
| /    |  GET |  Home Screen |
| /pre-process    | GET |  Pre processing of file from HD1 to HD2      |
| /loop   | GET | Processing of HD2 files and storing result in HD3 |

## Jupyter Notebook
- Open `http://localhost:8888/`
- Use `access_token` as password

## Minio
- Open `http://localhost:9000/`
- Use `access_token` as password

## Elastic Search
- Open `http://localhost:5601/`
- Use `access_token` as password


