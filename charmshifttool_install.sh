# This script will install the charm_shift_tool to a CERN
# openstack server. It is assumed that the server 
# is using a CC7 Extra x86_64# image

# Update all programs then install git
yum update
yum install git

# install davfs
yum install davfs

# add dfs to fstab and mount dfs
mkdir /dfs
https://dfs.cern.ch/dfs /dfs davfs user,noauto,file_mode=600,dir_mode=700 0 1

# install python3

# install python3-virtualenv

# Create a new charmshift user

# log into charmshift user
su charmshift

# create python3 virtualenv and install all dependencies

# download repository from github
git clone https://github.com/einoj/charm_shift_tool.git

#run charm_shift_tool and auto screenshot tool
