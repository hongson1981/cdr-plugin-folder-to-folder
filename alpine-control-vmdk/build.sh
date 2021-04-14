#!/bin/sh

_step_counter=0
step() {
	_step_counter=$(( _step_counter + 1 ))
	printf '\n\033[1;36m%d) %s\033[0m\n' $_step_counter "$@" >&2  # bold cyan
}


step 'Set up timezone'
setup-timezone -z UTC

step 'Set up networking'
cat > /etc/network/interfaces <<-EOF
	iface lo inet loopback
	auto eth0
  iface eth0 inet static
    address 192.168.1.1/24
    gateway 192.168.1.1
EOF
ln -s networking /etc/init.d/net.lo
ln -s networking /etc/init.d/net.eth0

step 'Adjust rc.conf'
sed -Ei \
	-e 's/^[# ](rc_depend_strict)=.*/\1=NO/' \
	-e 's/^[# ](rc_logger)=.*/\1=YES/' \
	-e 's/^[# ](unicode)=.*/\1=YES/' \
	/etc/rc.conf

step 'Install packages'
apk update
apk upgrade
apk add \
	chrony \
	less \
	logrotate \
	openssh \
	open-vm-tools \
	curl \
	make \
	dhcp \
	openssl \
  open-vm-tools \
	open-vm-tools-guestinfo \
  open-vm-tools-deploypkg

step 'Enable services'
rc-update add dhcpd default
rc-update add acpid default
rc-update add chronyd default
rc-update add crond default
rc-update add net.eth0 default
rc-update add net.lo boot
rc-update add termencoding boot
rc-update add open-vm-tools boot

# step 'Install Terraform'
# install /mnt/bin/terraform /usr/local/bin/terraform -o root -g root -m 0755 -D
# terraform version

# step 'Copy Terraform scripts'
# cp -rpf /mnt/terraform /opt/terraform
# cd /opt/terraform
# terraform init

step 'Generate DHCP config'
install -D -o root -g root -m 0644 /mnt/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf