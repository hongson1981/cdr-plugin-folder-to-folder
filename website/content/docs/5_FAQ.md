---
title: FAQ
weight: 6
---

# CONTENT
1. How to download rebuild file?
2. How to remove files form HD2 right after all files are processed?
3. How to change CDR Plugin VM, volume size to accommodate more testing files?
4. How to check which CDR Plugin version I am using?
5. How to check which GW SDK version I am using?
6. How to access Elastic and Kibana dashboards?
7. Where to find data sets for testing?
8. How to count the number of files being processed or created in HD2/HD3 directly from CDR VM?
9. How to deploy CDR Plugin VM in AWS?
10. How to deploy CDR Plugin in local?
11. How to SSH to deployed CDR Plugin VM?
12. When accessing Elastic getting an error "Could not locate that index-pattern-field (id: timestamp)"
13. How to retry to process files that were not sucesufully rebuilt?

---
---

### 1. How to download rebuild file?

- From Minio
   - Access the `Minio` from you browser
   - Navigate to scenario you run, choose HD3
   - Select file you want and download
- From CDR Plugin VM
   - ssh to CDR Plugin VM
   - Navigate to `/home/ubuntu/cdr-plugin-folder-to-folder/test_data` and go to scenario you run, choose HD3 and download file
   - Copy file to local
- From Jupyter
   - Access the Jupyter from you browser
   - Navigate to `data` folder
   - Choose scenario you run, choose HD3 and download file

![image (3)](https://user-images.githubusercontent.com/70108899/115361226-aa6d1380-a1c0-11eb-90e9-125ec4928c57.png)

- Once you open rebuild file, it will contain `Glasswall Processed` watermark

![image (2)](https://user-images.githubusercontent.com/70108899/115361164-988b7080-a1c0-11eb-821b-16e686328b90.png)

### 2. How to remove files form HD2 right after all files are processed?

- Within Jupyter Notebook, in `Work >Use Case 2` page set `clear_data` value
   - If `true` it will delete files from HD2 once they are all processed
   - If `false` it will leave the files in HD2

![image (1)](https://user-images.githubusercontent.com/70108899/115359812-50b81980-a1bf-11eb-9e03-db88266e2253.png)

### 3. How to change CDR Plugin VM, volume size to accommodate more testing files?

- Change your CDR Plugin VM, harddisk size (as per interface on ESXI or AWS)
- Connect to your VM and run bellow commands
```
> df -h //checks system in use for each volume
> lsblk //checks if volume has partition that needs to be extended
> sudo growpart /partition/to/extend  //specify partition that you want to extend ex. sudo growpart /dev/xvda 1
> sudo resize2fs /dev/root //extends dev/root volume which is where files are being stored
```
- Check for [more details](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/recognize-expanded-volume-linux.html) 
- AWS example
```
sudo growpart /dev/nvme0n1 1
sudo resize2fs /dev/root
```
![image](https://user-images.githubusercontent.com/70108899/116323891-47324100-a7bf-11eb-9f04-0053b66fe559.png)

- ESXI example
```
sudo growpart /dev/sda 1
sudo resize2fs /dev/root
```

### 4. How to check which CDR Plugin version I am using?
- From Swagger scroll to `Health Checks` section and run `/version` API call
- This will display CDR Plugin version currently used

### 5. How to check which GW SDK version I am using?
### 6. How to access Elastic and Kibana dashboards?
- Kibana Dashboard are stored in `https://github.com/filetrust/cdr-plugin-folder-to-folder-test-data` repo
- They are being automaticaly loaded
- In case you want to import/export custom one:
   - Navigate to Settings
   - Go to Stack Managment > Saved Objects and import/export dashboards you want

### 7. Where to find data sets for testing?

- Few example datasets can be found on: https://github.com/k8-proxy/data-sets/blob/main/README.md

### 8. How to count the number of files being processed or created in HD2/HD3 directly from CDR VM?

```
ls <folder path/name> | wc -l
ex. ls hd2 | wc -l
```

### 9. How to deploy CDR Plugin VM in AWS?
- Pick up latest CDR Plugin AMI id from github actions: https://github.com/filetrust/cdr-plugin-folder-to-folder/actions/workflows/cdr-plugin.yml
- Deploy AMI in AWS (t3.2x.large with corresponding tags and extend storage to at least 50GB)
- Deploy and use it
- In order to have latest changes within VM in cdr-plugin folder do git pull on the VM itself

### 10. How to deploy CDR Plugin in local?
- Prerequisite: Have Docker up and running
```
git clone https://github.com/filetrust/cdr-plugin-folder-to-folder.git
cd cdr-plugin-folder-to-folder
// set Minio and Jupyter password
export ACCESS_TOKEN=<your pass>
docker-compose up --build --force
```
- Access components from your browser using `<localhost>:<default_port>`
![image (5)](https://user-images.githubusercontent.com/70108899/117103199-2bf4a200-ad7a-11eb-9489-e4eaf8a30b43.png)

### 11. How to connect to deployed CDR Plugin VM?
- From the folder where your ssh key is stored run:
```
 ssh -L 8002:127.0.0.1:5601 -L 8001:127.0.0.1:8888 -L 8003:127.0.0.1:9000 -L 8000:127.0.0.1:8880 -L 8004:127.0.0.1:1313 -L 8005:127.0.0.1:8866 ubuntu@<VM IP>
```
- From browser you can now access:
   - Minio: `localhost:8003`
   - Jupyter: `localhost:8001`
   - Elastic: `localhost:8002`
   - Swagger: `localhost:8000/docs`
   - Hugo: `localhost:8004`
   - Voila: `localhost:8005`

### 12. When accessing Elastic getting an error "Could not locate that index-pattern-field (id: timestamp)" 
![image (5)](https://user-images.githubusercontent.com/70108899/115782913-824a0400-a3bc-11eb-822c-910c6248e491.png)

- SSH to your CDR Plugin VM
- Within `cdr_plugin_folder_to_folder` directory run `docker-compose down` 
- Once all components are down run `docker-compose up`
- Once all components are up, from your browser, go to Jupyter notebook and start any scenario you want
- Go back to Elastic > Discover and check the logs (error should not be there and logs should be visible)
- Make sure that you run some scenario before verifying that error is not present

### 13. How to retry to process files that were not sucesufully rebuilt?

- You executed the processing of original dataset (from Hugo: clear > load > start processing)
- In Minio,verify that you have files present in `hd2 > data`
- Start the processing again, with just `start processing` do not clear or load data again
- This will pick up files from `hd2 > data` and process them again