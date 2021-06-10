---
title: Deploy CDR Plugin in ESXi
weight: 3
---
## Offline deployment flow using OVAs

![image](https://user-images.githubusercontent.com/70108899/117101826-56912b80-ad77-11eb-9fa6-584f409b5168.png)

---
---

## Deploying Workflow Cluster OVA

- Login to  VMWare ESXi console
   - Select Virtual machines > Create / Register VM > Deploy a virtual machine from OVF or OVA file

  ![image](https://user-images.githubusercontent.com/70108899/114046803-6f4a1680-9889-11eb-93be-0ba78276671e.png)

- Browse and import OVA (downloaded from S3 bucket)
  ![image](https://user-images.githubusercontent.com/70108899/114052179-1af56580-988e-11eb-8cc9-cd6c2ee26c48.png)
- Leave default data storage 
- Set VM adapter. 
   - **Note**: On your ESXI  Server, make sure the network adapter is set correctly and created VM is assigned to the corresponding adapter. 
- Start the VM deployment
  ![image](https://user-images.githubusercontent.com/70108899/114047499-031be280-988a-11eb-8bc0-f09ab491f988.png)
- Wait until VM is deployed
- Start the VM and open the console
  ![image](https://user-images.githubusercontent.com/70108899/114047708-2e063680-988a-11eb-941a-b05c0c9c84ea.png)
- Wait until VM is started. This may take up to several minutes
- Once login prompt appears on the terminal, login with provided credentials
- In cmd type `wizard`
- Configure Network > Change IP, Gateway, and DNS (navigate using up down buttons, then tab to go to submit) 
    - **Note**: Configure GW_SDK_VM with same subnet as the machine which is running Glasswall Desktop App to use Off-line
  
  ![image](https://user-images.githubusercontent.com/70108899/114047817-45ddba80-988a-11eb-98b8-8c85aa4c74e0.png)
- Give the VM ~10 minutes before jumping to usage
- In cmd run `ip -4 a` to verify that correct IP is set
  ![image](https://user-images.githubusercontent.com/70108899/114048052-7faec100-988a-11eb-819f-ddf211b916f6.png)

---
---

## Deploying Worker Cluster OVA
- Follow the same steps as for Deploying Workflow Cluster OVA 
- Start the VM deployment
  ![image](https://user-images.githubusercontent.com/70108899/114047499-031be280-988a-11eb-8bc0-f09ab491f988.png)

- Wait until VM is deployed
  ![image](https://user-images.githubusercontent.com/70108899/114047591-14fd8580-988a-11eb-8327-7825fa778071.png)

- Once VM is deployed go to edit settings:
   - Set VM CPUs to 4
   - Set RAM to 8gB
  
  ![image](https://user-images.githubusercontent.com/70108899/114286820-6c564e00-9a62-11eb-86bf-47b63028f15d.png)

- Start the VM and open the console
  ![image](https://user-images.githubusercontent.com/70108899/114047708-2e063680-988a-11eb-941a-b05c0c9c84ea.png)

- Wait until VM is started. This may take up to several minutes
- Once login prompt appears on the terminal, login with provided credentials
- In cmd type `wizard`
- Configure Network > Change IP, Gateway, and DNS (navigate using up down buttons, then tab to go to submit) 
    - **Note**: Configure GW_SDK_VM with same subnet as the machine which is running Glasswall Desktop App to use Off-line
  
  ![image](https://user-images.githubusercontent.com/70108899/114047817-45ddba80-988a-11eb-98b8-8c85aa4c74e0.png)

- Give the VM ~10 minutes before jumping to usage
- In cmd run `ip -4 a` to verify that correct IP is set

  ![image](https://user-images.githubusercontent.com/70108899/114048052-7faec100-988a-11eb-819f-ddf211b916f6.png)

- In case you want to change share VM password, run previous steps just instead Configure Network go to Change Password > Type new password

## Deploying Desktop OVA
- Follow the same steps as in previous sections
- Start the VM deployment
 ![image](https://user-images.githubusercontent.com/70108899/114047499-031be280-988a-11eb-8bc0-f09ab491f988.png)

- Wait until VM is deployed
 ![image](https://user-images.githubusercontent.com/70108899/114047591-14fd8580-988a-11eb-8327-7825fa778071.png)

- Open the VM console
 ![image](https://user-images.githubusercontent.com/70108899/114047708-2e063680-988a-11eb-941a-b05c0c9c84ea.png)

- Wait until VM is up and running. This may take up to several minutes
- Once login prompt appears on the terminal, login with provided credentials
- Configure Network: 
   - In cmd run `nmcli con mod Wired\ connection\ 1 ipv4.addresses <GW SDK IP> ipv4.gateway 192.168.30.1 ipv4.dns 8.8.8.8 ipv4.method auto`, which will configure VM IP and Default Gateway
     ```    
     Example: nmcli con mod Wired\ connection\ 1 ipv4.addresses 192.168.30.112/24 ipv4.gateway 192.168.30.1 ipv4.dns 8.8.8.8 ipv4.method auto
     ```
   - Run `ip -4 a` to verify that correct IP is set

  ![image](https://user-images.githubusercontent.com/70108899/114048052-7faec100-988a-11eb-819f-ddf211b916f6.png)

- Configure Host file:
   - In cmd run `sudo nano /etc/hosts` and update IP addresses:
      - Next to `gw-sdk.local` update `GW-SDK-VM IP` 
   - For accessing CDR Plugin components next to `jupyter.local` line update `CDR Plugin VM IP`
  ![](https://github.com/filetrust/cdr-plugin-folder-to-folder/blob/main/img/2021-04-09_14h21_58.png)
   - Once the IPs are updated Press `CTRL + X` and press `Y` to save the new config

- Access Swagger UI, Minio, Jupyter Notebooks and Elastic
   - Make sure above `hosts file` is configured
   - On Glasswall Desktop VM, open Firefox
   - In the Bookmarks bar you will find links to `Swagger UI`, `Minio`, `Jupiter Notebooks` and `Elastic`.

  ![](https://github.com/filetrust/cdr-plugin-folder-to-folder/blob/main/img/2021-04-09_14h29_31.png)

### Run Glasswall Desktop App
- Access Desktop VM
- Open Terminal and Navigate to Desktop/Glasswall Desktop App and run below command
 ```
 ./glasswall-desktop-1.0.5.AppImage
 ```
- Once you run above command you will see Glasswall Desktop App running
  ![image](https://user-images.githubusercontent.com/70108899/114049412-b933fc00-988b-11eb-86b1-25f5b3929810.png)

- On how to **Integrate Glasswall Desktop App and Glasswall SDK** check instructions [here](https://github.com/filetrust/cdr-plugin-folder-to-folder/wiki/Integrate-Glasswall-Dektop-App-to-GW-SDK-VM)



## Online deployment on ESXI

- In above steps when configuring network, instead of using the setup that is not exposed to the outside world, set valid IP, Gateway and DNS 