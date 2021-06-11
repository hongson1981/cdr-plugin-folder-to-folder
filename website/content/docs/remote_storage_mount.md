---
title: Remote Storage Mount
weight: 9
--- 

# S3 Mount

- Download rclone
```
curl https://rclone.org/install.sh | sudo bash
```
- Run 
`rclone config
`
- Enter below values 

```
    n/s/q>                 -  n 
    name>                  -  <remote_name>  ( any name )
    Storage                - 4
    provider               - 1
    env_auth               - 1 and give aws access key and secret key
    region                 - <blank>
    endpoint               - <blank>
    location_constraint    - <blank>
    acl                    - 2 ( depends on use case )
    server_side_encryption - 2
    sse_kms_key_id         - 2
    storage_class          - 2 ( depends on use case )
    Edit advanced config?  - n
    <y/e/d>                 - n

```

- Verify s3 is connected by listing all buckets `rclone lsd <Name>:`  
  Example   `rclone lsd remote_s3:`
  
- Copy and Sync Commands from s3 to local

    ```
    rclone copy <remote_name>:<Bucket_Name>/<folder> <local_destination_location>
    rclone sync -i <remote_name>:<Bucket_Name>/<folder> <local_destination_location>
  ```
  
- Copy and Sync Commands from local to s3

    ```
    rclone copy <local_destination_location> <remote_name>:<Bucket_Name>/<folder>
    rclone sync -i  <local_destination_location> <remote_name>:<Bucket_Name>/<folder>
  ```
  
- Mount from s3 to local

    ```
    rclone mount <local_destination_location>  <remote_name>:<Bucket_Name>/<folder> --daemon 
   ```
  
- Mount from local to s3

    ```
    rclone mount <local_destination_location> <remote_name>:<Bucket_Name>/<folder> --daemon 
   ```
  
- Create bucket
```
rclone mkdir <remote_name>:<bucket_name>
```
- For more details Follow doc `https://rclone.org/s3/`

