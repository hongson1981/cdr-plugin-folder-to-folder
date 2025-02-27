---
title: End to End Workflow on ESXI
weight: 5
---

## Parts of the End to End Workflow - ESXI
- Worker cluster = Glasswall SDK OVA
- Workflow cluster = CDR Plugin OVA
- Glasswall Desktop OVA

On previous pages you can find `how to deploy` each of these 3 as a separate VMs.
Have them ready and have their IPs available.
All 3 VMs should be in the same Network, as that will enable their offline, mutual communication.

- Deploy `Glasswall SDK` VM
- Deploy `CDR Plugin` VM
- Deploy `Glasswall Desktop` VM
   - Within VM: Update hosts file with Glasswall SDK ip and CDR Plugin VM ip, by running `sudo nano /etc/hosts` and update IP addresses:
      - Next to `gw-sdk.local` update `GW-SDK-VM IP`
      - For accessing CDR Plugin components, next to `jupyter.local line` change `CDR Plugin VM IP`
      - ![](https://github.com/filetrust/cdr-plugin-folder-to-folder/blob/main/img/2021-04-09_14h21_58.png)
      - Once the IPs are updated Press `CTRL + X` and press `Y` to save the new config
   - On Glasswall Desktop VM, open Firefox
   - In the Bookmarks bar you will find links to `Swagger UI`, `Minio`, `Jupiter Notebooks` and `Elastic`.

## Use Minio

- Open the `MinIO Browser` bookmark
   - Login to Minio
      - **Credentials can be found on VM Desktop in `password.txt` along with others**
   - Within Minio you will have 2 testing scenarios.
       - Scenario 1 having just one file in HD1
       - Scenario 2 having multiple files and subfolders in HD1
   - ![image](https://user-images.githubusercontent.com/70108899/114287415-e983c200-9a66-11eb-91da-843097de1f7e.png)
   - Under each of testing scenarios along with HD1 you will find HD2 and HD3 folders
       - HD2 contains original file data (hash folder with metadata and source) and statuses (hash.json)
       - HD3 contains rebuild file
   - In order to have clean start, you can go ahead and delete all content from HD2 and HD3
   - Or you can upload the files (drag and drop in HD1 folder), if you want to test and follow along
      - Note: On VM Desktop you can find folder `date-set` with example testing files

## Run tests using Jupyter Notebook

- Open Jupiter Notebook bookmark in Desktop VM Browser
- Login to Jupyter notebook using password specified in `password.txt`
- There are two folders in the root
    - test_data
        - scenario-1 and scenario-2
            - hd1   -   Source Data which has original files
            - hd2   -   Evidence/Transfer Data which has metadata ,report and source file
            - hd3   -   Target Data which has rebuilt file in same folder structure as hd1
    - work - Contains Jupyter notebook execution codes

### Jupyter: Use case 1
- Navigate to `Work>Use case 1 - Setup vars - Process files`
- Follow the steps below or point to the [video](https://www.youtube.com/watch?v=C6nGHd6DbgY&ab_channel=GlasswallEngineering)
- **Step 1**: Configure server and check health check
   - Select code box and press `RUN` from top bar
   - ![image](https://user-images.githubusercontent.com/70108899/114384387-ed126880-9b8e-11eb-911c-b28376b0fca3.png)
- **Step 2**: Configure hard disks
   - Modify data sections to corresponds to data paths you are using (in case you are using Minio change scenarios)
   - Select code box and press `RUN` from top bar
   - Wait to see response
   - ![image](https://user-images.githubusercontent.com/70108899/114384604-382c7b80-9b8f-11eb-97bd-d66760015437.png)
- **Step 3**: Configure GW SDK Endpoints
   - Modify `IP` to corresponds to GW SDK IP you are using
   - Select code box and press `RUN` from top bar
   - Wait to see response
   - ![image](https://user-images.githubusercontent.com/70108899/114384758-6f9b2800-9b8f-11eb-9977-392c20ecf7bb.png)
- **Step 4**: Process files
   - Select code box and press `RUN` from top bar
   - Wait to see response
   - ![image](https://user-images.githubusercontent.com/70108899/114384851-8d688d00-9b8f-11eb-9ac3-86dc517f7f5e.png)
- Your file should be processed now. If you used Minio (scenario 1 or 2, or another data foleder created in Minio), you can navigate back to Minio and verify that files are processed and that rebuild file is located in HD3 folder
 
### Jupyter: Use case 2

- Navigate to `Work>Use case 2 - Process files`
- Follow the steps below or point to the [video](https://www.youtube.com/watch?v=VVLtm7BAK9A)
- Modify `sdk_endpoints` in Jupyter box. Specify `GW SDK IP` you are using.
- You can also modify `base_folder` and  `data_paths` to use specific files for your testing (or add/remove files directly on Minio)
- ![image](https://user-images.githubusercontent.com/70108899/114375743-470e3080-9b85-11eb-9fed-121fe481cd85.png)
- Trigger test execution by pressing `RUN` from top bar
- Wait until it is all processed and until you get tree structure 
- ![image](https://user-images.githubusercontent.com/70108899/114376283-c6036900-9b85-11eb-9560-d5ac0ac85a4e.png)
- If you used default data for testing you can navigate back to Minio and verify that files are processed and that rebuild file is located in HD3 folder

## Run tests using Swagger

- From `Desktop VM` open the browser
- Navigate to `FastAPI - Swagger UI` bookmark
   - On the page you will find documentation about each fastAPI call with number steps on how to follow
   - ![image](https://user-images.githubusercontent.com/70108899/114287519-b7269480-9a67-11eb-82a1-d8e7f4bd57a1.png)
   - To test `CDR plugin folder to folder` solution
       - **Step 0**: Configuration
          - Execute `/configuration/configure_env` API that will set hard discs. Default is set to Minio Scenario 1 but here you can switch to Scenario 2 or any other you create
          - Execute `/configuration/configure_gw_sdk_endpoints` API, provide `GW SDK IP` and set port to `8080`
       - **Step 1**: Pre Processor
          - Execute `/pre-processor/pre-process` API and verify that response status code is 200
       - **Step 2**: Processing
          - Execute `/processing/start` API and verify that response status code is 200
       - **Step 3**: Go back to Minio, and under scenario 1 (or any other you used) you should be able to see HD2 and HD3 having the data and original file being rebuilt
  
