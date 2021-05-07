![OvaToEsxiDeploy-new-4May21](https://user-images.githubusercontent.com/78961055/117029580-6deefb00-ad1c-11eb-995c-95ea64851069.png)


Automated deployment of OVAs in to ESXi
===
## 1. On your computer, download below OVAs from S3 bucket.
       Installer.ova
       SDK.ova
       Workflow.ova
      
## 2. Import Installer OVA to ESXi
```shell
 2.1. Login to ESXi webconsole --> Click on Virtual Machines-->Click on Create or Register VM
 2.2. On the New Virtual Machine window, select creation type as “Deploy a virtual machine from an OVF or OVA file” and click Next
 2.3. Enter the name for the virtual machine and click on "select files or drag/drop" and select Installer OVA then click Next
 2.4. Select storage and click Next,
 2.5. Select VM network and click next
 2.6. Click on Finish
```
## 3. Configure Network
```shell
 3.1.In cmd run nmcli con mod Wired\ connection\ 1 ipv4.addresses <GW SDK IP> ipv4.gateway 192.168.30.1 ipv4.dns 8.8.8.8 ipv4.method auto
        Example: nmcli con mod Wired\ connection\ 1 ipv4.addresses 192.168.30.112/24 ipv4.gateway 192.168.30.1 ipv4.dns 8.8.8.8 ipv4.method auto
        This will configure VM IP and Default Gateway

 3.2.In cmd run ip -4 a to verify that correct IP is set
       
```
![ConfigureNetwork-new-7May21](https://user-images.githubusercontent.com/70108899/114048052-7faec100-988a-11eb-819f-ddf211b916f6.png)

## 4. Copy SDK and Workflow OVAs to ESXi datastore
```shell
 4.1. Login to ESXi web console 
 4.1.1. Click on Storage-->datastore1 (or any storage of your choice)-->Datastore Browse-->Select the Installer folder and create directory with name "OVAs" 
 4.1.2. Click on OVAs directory and click on Upload, and then upload sdk.ova and workflow.ova
```
## 5. Install sshfs and mount datastore to Installer VM
```shell
 5.1. Open terminal from Installer VM and Create directory OVAs under $HOME
          mkdir $HOME/OVAs
          cd $HOME/OVAs
 5.2. Validate sshfs tool and mount datastore
          sshfs --version
          sshfs root@esxi01.glasswall-icap.com:/vmfs/volumes/datastore1/Installer/OVAs /home/ubuntu/OVAs/
          cd $HOME
          ls /home/ubuntu/OVAs/
```
## 6. Terraform Deployment
 ```shell
 6.1. Validate ovftool
Login to Installer VM and issue below command,
          ovftool --version
```
 ```shell
 6.2. Make a copy of *secret.auto.tfvars.example* and place your credentials.
         cd $HOME/ubuntu/cdr-plugin-folder-to-folder/infra/terraform/esxi/tfvars/
         

cp secret.auto.tfvars.example secret.auto.tfvars
```
update details as require in secret.auto.tfvars

Now, we have to initialize Terraform.

Configure VMs details using secret.auto.tfvars. See an example at *infra/terraform/esxi/tfvars/secret.auto.tfvars.example*. See the list of variables below.

|        Variable             |     Description                           |
| ---------------------------:| ------------------------------------------|
| ssh_credentials             | ESXi SSH connection details               |
| instance_count              | Count of instances                        |
| name_prefix                 | Name prefix for the instances             |
| datastore                   | Datastore name                            |
| ovf_source                  | Local path or URL to OVF                  |
| network                     | Network name                              |
| vcpu_count                  | Count of vCPU per instance                |
| memory_mib                  | Count of RAM per instance in MiB          |
| auto_power_on               | Will power on instances if true           |
| boot_disk_size              | HDD size of GiB                           |
| sdk_ip_addresses_esxi1      | Enter SDK IP address of esxi1             |     
| sdk_gateway_esxi1           | Enter SDK gateway of esxi1                |         
| workflow_ip_addresses_esxi1 | Enter Workflow IP address of esxi1        |
| workflow_gateway_esxi1      | Enter Workflow gateway of esxi1           |   
| od_ip_addresses_esxi1       | Enter OD IP address of esxi1              |     
| od_gateway_esxi1            | Enter OD gateway of esxi1                 |          
| sdk_ip_addresses_esxi2      | Enter SDK IP address of esxi2             |    
| sdk_gateway_esxi2           | Enter SDK gateway of esxi2                |       
| od_ip_addresses_esxi2       | Enter OD IP address of esxi2              |    
| od_gateway_esxi2            | Enter OD gateway of esxi2                 |         
| workflow_gateway_esxi2      | Enter Workflow IP address of esxi2        |  
| workflow_ip_addresses_esxi2 | Enter Workflow gateway of esxi2           |

 
 6.3. Terraform_apply

once the value is updated in secret.auto.tfvars run

```shell
cd ..
terraform init -var-file=./tfvars/secret.auto.tfvars
```
run terraform plan to validate the code

```shell
terraform plan -var-file=./tfvars/secret.auto.tfvars
```
run terraform apply to deploy the VMs

```shell
terraform apply -var-file=./tfvars/secret.auto.tfvars
```

6.4. Terraform_destroy

once the value is updated in secret.auto.tfvars run

```shell
cd $HOME/ubuntu/cdr-plugin-folder-to-folder/infra/terraform/esxi
terraform destroy -var-file=./tfvars/secret.auto.tfvars
```
===

## 2. VMDK

> See an example in vmdk.tf.example

### 2.1. Configuration

Make a copy of *secret.auto.tfvars.example* and place your credentials.

```shell
cp -pv secret.auto.tfvars.example secret.auto.tfvars
"${VISUAL}" secret.auto.tfvars
```

Now, we have to initialize Terraform.

```shell
terraform init -upgrade
```

Configure VMs modules using variables from esxi-instance module. See an example at *esxi-instance/variables.tf*. See the list of variables in *variables.tf* or refer to the table below.

|        Variable | Description                      |
| --------------: | -------------------------------- |
| ssh_credentials | ESXi SSH connection details      |
|  instance_count | Count of instances               |
|     name_prefix | Name prefix for the instances    |
|       datastore | Datastore name                   |
|            vmdk | Path to vmdk in datastore        |
|         network | Network name                     |
|             cpu | Count of vCPU per instance       |
|             ram | Count of RAM per instance in MiB |

## 3. Apply

Now you can apply the changes.

```shell
terraform apply
```
