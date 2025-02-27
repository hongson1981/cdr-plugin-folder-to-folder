---
title: New workflows
weight: 8
---
# CONTENT
### 1. Retry workflow
### 2. Uploading the zip file via URL
### 3. Setting the number of threads for pre processing
### 4. Checking the CDR plugin/ GW SDK version
### 5. Processed File Dashboard
### 6. Threat Analysis Dashboard

---
---

## 1. Retry workflow

**Context**: 
- After running CDR F2F processing of specific scenario, rerun the scenario for failed files.

**Steps**:
- Run CDR F2F processing (CLEAR > LOAD > START)
- After processing is done verify the number and context of failed files
- Rerun CDR F2F processing (START)
- Verify the number and context of failed files

**Goal**:
- Number of failed files (if their failure is connected to GW SDK rather than Rebuild engine) is lower
- Come to a number of files for which processing fails due to specific Rebuild Engine error

---
---

## 2. Uploading the zip file via URL

**Context**
- Be able to directly add files via zip URL, import and pre process it

**Steps**
- Create scenario folder in cdr_plugin_folder_to_folder/test_data
- Create hd1, hd2, hd3 subfolders
- Go to CDR Plugin UI and in the Workflows set above folder as default
- Go to Swagger, find an API `/pre-processor/download_and_pre_process_a_zip_file`
  ![image](https://user-images.githubusercontent.com/70108899/119680626-a8424880-be41-11eb-8882-aead32dce4c6.png)
- Pass the URL of the zip file you want to process (zip file URL can be any)

**Goal**

- Once API is executed, zip file will be unzipped and all files will be present and hd1 folder
- Files will be pre processed and present in hd2/todo folder
- Original zip file will be deleted

---
---

## 3. Setting the number of threads for pre processing

**Context**
- Improve the performance of the pre-processing
**Steps**
- Go to CDR Plugin UI
- Set base dir to a scenario you want to process
- Go to Swagger and find API `/pre-processor/pre-process`
- Set the number of threads you would like to use for pre-processing of your files
![image](https://user-images.githubusercontent.com/26714598/120308216-e7aae200-c2e4-11eb-9e2a-e0b4c0ea6d45.png)

**Goal**
- Pre-processing (LOAD) is done way faster, depending on scenario size, in couple of minutes

---
---

## 4. Check the CDR plugin/ GW SDK version

**Context**
- Check the CDR Plugin version to make sure you are using the latest release
- Check GW SDK version to check that you are up to date with the recent changes

**Steps**
- Navigate to Swagger and under `Health Check` section find `/version` API
- Run API and see current CDR Plugin version
  ![image](https://user-images.githubusercontent.com/70108899/120822236-7ecaa080-c556-11eb-962e-9b971a9c4ee4.png)

- For GW SDK version navigate to `<GW SDK API>:8080` and under `Detail` section find `/api/detail/version` API
- Run API and see current GW SDK version
  ![image](https://user-images.githubusercontent.com/70108899/120822638-e97bdc00-c556-11eb-94ba-b0451f7e7f66.png)

---
---

## 5. Processed File Dashboard

**Context**
- Get information about current run for processing data
- Have first hand metrics

**Steps**
- Go to CDR Plugin UI
- Set base dir to a scenario you want to process
- Run CDR F2F processing (CLEAR > LOAD > START)
- Navigate to `Processed Files v8` Dashbord
- Check processing metrics:
   - Rebuild status (initial, in progress, rebuild successfull, failed to rebuild, not supported or no cleaning needed)
   - File type extensions 
   - GW SDK servers and request distribution
   - Average/per minute processing duration
   - Bandwith
   - Original and Rebuild total size of files

  ![image](https://user-images.githubusercontent.com/70108899/120897678-b35a5d00-c627-11eb-8929-11b2dce30020.png)


---
---

## 6. Threat Analysis Dashboard

**Context**
- Run threat analysis on processed data
- Have first hand metrics about threats in each of the files

**Steps**
- Data processing is done
- Navigate to `File Analysis - Threat Level` Dashbord from CDR Plugin UI
- Check metrics:
   - Distribution of file types
   - Threat level % (low, meddium, high)
   - Number of files that contain: macros, comments, javascripts and/or URLs

  ![image](https://user-images.githubusercontent.com/70108899/120897383-282c9780-c626-11eb-983e-4acd53988f6c.png)
- Check details about sanitized and remmidiated issues

  ![image](https://user-images.githubusercontent.com/70108899/120897452-88bbd480-c626-11eb-8bc3-de27d6fe6456.png)