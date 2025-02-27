---
title: End to End Workflow on AWS
weight: 4
---

## Parts of the End to End Workflow - AWS
- Worker cluster = Glasswall SDK AMI
- Workflow cluster = CDR Plugin AMI

## Prerequisites 
- Deploy `Glasswall SDK` VM
  - You can reuse already deployed GW SDK VMs (IPs)
  - You can use and you should use more than one GW SDK VM (depending on amount of data you are testing)
- Deploy `CDR Plugin` VM
  - You can use [this video](https://www.loom.com/share/ab2b8904104843c5af424484c57a380a) as a reference
- SSH to your CDR Plugin VM
  - Run following command: `ssh -L 8002:127.0.0.1:5601 -L 8001:127.0.0.1:8888 -L 8003:127.0.0.1:9000 -L 8000:127.0.0.1:8880 -L 8004:127.0.0.1:1313 -L 8005:127.0.0.1:8866 ubuntu@<cdr_plugin_ip>`
  - Above command will map default ports to the ones you can use to access components local via `localhost:<port>`
  
  ![image (5)](https://user-images.githubusercontent.com/70108899/117103199-2bf4a200-ad7a-11eb-9489-e4eaf8a30b43.png)
  - You can use [this video](https://www.loom.com/share/ab2b8904104843c5af424484c57a380a) as a reference

## Components overview
  
- ![image (4)](https://user-images.githubusercontent.com/70108899/117103089-f64fb900-ad79-11eb-9d1a-a2b51b3d2123.png)

## Use Hugo

- Open the website by accessing `localhost:8004`
  ![image](https://user-images.githubusercontent.com/70108899/117105827-19c93280-ad7f-11eb-97ab-194197127b69.png)
- Navigate to `Workflows>folder-to-folder`
  ![image](https://user-images.githubusercontent.com/70108899/117105917-45e4b380-ad7f-11eb-83d5-f435693f275b.png)
- `Set base dir` to corresponding folder on Minio you want to test.
  - Verify in the output that folder is set
  
  ![image](https://user-images.githubusercontent.com/70108899/117106068-83494100-ad7f-11eb-9fbc-7a9f95a1fc89.png)
- Navigate to `Set IPs`
  - Click on `Load from AWS`. This will load GW SDK IPs currently deployed on AWS
  - Click on `Set plugin IPs` to assign previously loaded IPs to CDR Plugin to use
  
  ![image](https://user-images.githubusercontent.com/70108899/117106254-d58a6200-ad7f-11eb-8b92-4da2a743e3de.png)
- Navigate to `Workflows>folder-to-folder`
  - Set base dir one more time
  - Click on `clear data` to clean HD2 and HD3 folders and have clean start
  - Click on `load files`
  - Press `load` button in the left corner to refresh the Dashboard
    - In below screen select `Processed Files v8` Kibana Dashboard
    - Once files are loaded Dashboard should reflect that
    - Use `Refresh` button within Kibana to follow with most recent changes
  
  ![image](https://user-images.githubusercontent.com/70108899/117106668-8f81ce00-ad80-11eb-8bf2-97e90146138e.png)
    - Once processing is done you can select `File Analysis - Threat Level` Dashboard to see the analysis
- Navigate to `Status` to check latest processing status
- Navigate to `Servers` to access FastAPI, Jupyter, Minio and Elastic
- Navigate to `Docs` to check latest documentation
- Follow along with [this video](https://user-images.githubusercontent.com/70108899/117102137-f5b62300-ad77-11eb-92b9-c377b7261618.mp4) as it covers above details

## How individual components are used? 
- All components below now can be reached within Hugo and used from there
- They can also be accessed individually from the browser 
- Jupyter notebook is completely integrated with Voila into Hugo so it can be used directly from `Workflow>folder-to-folder` page providing better user experience
- Kibana Dashboards are visible from `Workflow>folder-to-folder` page

## Use Minio

- Open the `MinIO` by accessing `localhost:8003`
   - Login to Minio with provided credentials
   - Within Minio you will have 2 testing scenarios.
       - Scenario 1 having just one file in HD1
       - Scenario 2 having multiple files and subfolders in HD1
  
  ![image](https://user-images.githubusercontent.com/70108899/114287415-e983c200-9a66-11eb-91da-843097de1f7e.png)
   - Under each of testing scenarios along with HD1 you will find HD2 and HD3 folders
       - HD2 contains original file data (hash folder with metadata and source) and statuses (hash.json)
       - HD3 contains rebuild file
   - In order to have clean start, you can go ahead and delete all content from HD2 and HD3
   - Or you can upload the files (drag and drop in HD1 folder), if you want to test and follow along
      - Data set examples can be found [here](https://github.com/k8-proxy/data-sets)


## Run tests using Jupyter Notebook

- Open Jupiter Notebook by accessing `localhost:8001` within your browser
- Login to Jupyter notebook with provided credentials
- There are two main folders in the root
    - test_data
        - scenario-1 and scenario-2
            - hd1   -   Source Data which has original files
            - hd2   -   Evidence/Transfer Data which has metadata ,report and source file
            - hd3   -   Target Data which has rebuilt file in same folder structure as hd1
    - work - Contains Jupyter notebook execution codes
 
### Jupyter: Use case 2

- Navigate to `Work>Use case 2 - Process files`
- Follow the steps below or point to the [video](https://www.youtube.com/watch?v=VVLtm7BAK9A)
- Modify `ips` in Jupyter box. Specify `GW SDK IP` you are using.
- You can also modify `base_folder` and  `data_paths` to use specific files for your testing (or add/remove files directly on Minio)
  ![image](https://user-images.githubusercontent.com/70108899/114375743-470e3080-9b85-11eb-9fed-121fe481cd85.png)
- Trigger test execution by pressing `RUN` from top bar
- Wait until it is all processed (process bar is full) and you get tree structure 
  ![image](https://user-images.githubusercontent.com/70108899/114376283-c6036900-9b85-11eb-9560-d5ac0ac85a4e.png)
- If you used default data for testing you can navigate back to Minio and verify that files are processed and that rebuild file is located in HD3 folder

## Run tests using Swagger

- Open Swagger by accessing `localhost:8000` within your browser
   - On the page you will find documentation about each fastAPI call with number steps on how to follow
  
  ![image](https://user-images.githubusercontent.com/70108899/114287519-b7269480-9a67-11eb-82a1-d8e7f4bd57a1.png)
   - To test `CDR plugin folder to folder` solution
       - **Step 0**: Configuration
          - Execute `/configuration/configure_env` API that will set hard discs. Default is set to Minio Scenario 1 but here you can switch to Scenario 2 or any other you create
          - Execute `/configuration/configure_gw_sdk_endpoints` API, provide `GW SDK IP` and set port to `8080`
       - **Step 1**: Pre Processor
          - Execute `/pre-processor/pre-process` API and verify that response status code is 200
       - **Step 2**: Processing
          - Execute `/processing/start` API and verify that response status code is 200
       - **Step 3**: Go back to Minio, and under scenario 1 (or any other you used) you should be able to see HD2 and HD3 having the data and original file being rebuilt
  




