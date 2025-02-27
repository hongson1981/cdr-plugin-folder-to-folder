---
title: Deploy CDR Plugin in AWS
weight: 2
---

## Deploying CDR Plugin on AWS

- Use latest CDR Plugin AMI.
   - AMI ID can be found in github actions: https://github.com/filetrust/cdr-plugin-folder-to-folder/actions/workflows/cdr-plugin.yml
- Login to AWS Console
- Navigate to AWS > AMIs
- Search for the AMI with specific ID from the first step (make sure you are in correct region)
- From AMIs workspace click on specific AMI > Choose `Launch`
- Set instance type to `t3.2x.large` and extend storage to at least `50GB` (in case you are planning to test large data sets set storage to higher value)
- Add any tags if needed
- Add security group if needed (for CDR by default nothing additional should be set)
- Click on `Review and Launch`
    - Select `Create or use existing key pair` [Note: Key is not needed for SSH at the moment]
- Wait for instance to be initialized (~10 minutes) and use public IP to access CDR Plugin VM
- SSH to your instance (password will be shared):
```
ssh -L 8002:127.0.0.1:5601 -L 8001:127.0.0.1:8888 -L 8003:127.0.0.1:9000 -L 8000:127.0.0.1:8880 -L 8004:127.0.0.1:1313 -L 8005:127.0.0.1:8866 ubuntu@<VM IP>
```
- From browser you can now access:
   - Minio: `localhost:8003`
   - Jupyter: `localhost:8001`
   - Elastic: `localhost:8002`
   - Swagger: `localhost:8000/docs`
   - Hugo: `localhost:8004`
- Main UI to use is: `localhost:8004`

## Set CDR Plugin to work offline on AWS
- EC2 > Navigate to your instance > Under your Instance Summary > Security
![security-tab](https://user-images.githubusercontent.com/60857664/108712705-d735df00-751f-11eb-9bdb-388cbf43a687.png)
- Security Details > Security Groups > Click on `sg-...` (your launch-wizard)
- Outbound rules tab > Edit outbound rules > Delete the outbound rule & save rules
![Screenshot from 2021-02-22 15-18-03](https://user-images.githubusercontent.com/60857664/108713672-36e0ba00-7521-11eb-93d1-e10246562216.png)
