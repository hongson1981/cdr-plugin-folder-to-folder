#!/bin/bash
set -v -e

pushd $( dirname $0 )
if [ -f ./env ] ; then
source ./env
fi

# set hostname
sudo hostnamectl set-hostname glasswall

# get source code
cd ~
BRANCH=${BRANCH:-main}
GITHUB_REPOSITORY=${GITHUB_REPOSITORY:-filetrust/cdr-plugin-folder-to-folder}
git clone https://github.com/${GITHUB_REPOSITORY}.git --branch $BRANCH --recursive && cd cdr-plugin-folder-to-folder

# build docker images
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    open-vm-tools \
    open-vm-tools-desktop \
    sshfs \
    zip \
    software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install docker-ce docker-ce-cli containerd.io -y
#sudo curl -L "https://github.com/docker/compose/releases/download/1.29.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
#sudo chmod +x /usr/local/bin/docker-compose

# install vmware tools
#sudo apt install open-vm-tools
#sudo apt install open-vm-tools-desktop -y
curl -sSL https://raw.githubusercontent.com/vmware/cloud-init-vmware-guestinfo/master/install.sh | sudo sh -

#Install OVF Tools 
wget https://github.com/filetrust/cdr-plugin-folder-to-folder/tree/main/infra/terraform/esxi/artifacts/VMware-ovftool-4.4.1-16812187-lin.x86_64.bundle
chmod 755 VMware-ovftool-4.4.1-16812187-lin.x86_64.bundle
sudo ./VMware-ovftool-4.4.1-16812187-lin.x86_64.bundle
ovftool --version

#Install Terraform Latest version == verified
wget https://releases.hashicorp.com/terraform/0.15.3/terraform_0.15.3_linux_amd64.zip
#sudo apt-get install zip -y
unzip terraform*.zip
sudo mv terraform /usr/local/bin
terraform version
rm terraform*.zip

#Install sshfs
#sudo apt -y install sshfs
sshfs --version

#Install Postman
sudo snap install postman

# allow password login (useful when deployed to esxi)
SSH_PASSWORD=${SSH_PASSWORD:-glasswall}
printf "${SSH_PASSWORD}\n${SSH_PASSWORD}" | sudo passwd ubuntu
sudo sed -i "s/.*PasswordAuthentication.*/PasswordAuthentication yes/g" /etc/ssh/sshd_config
sudo service ssh restart