# This script will install the charm_shift_tool to a CERN
# openstack server. It is assumed that the server 
# is using a CC7 Extra x86_64# image

# Update all programs then install git
yum -y update
yum -y install git

# install davfs
yum -y install davfs2

# add dfs to fstab and mount dfs
mkdir /dfs
echo "https://dfs.cern.ch/dfs /dfs davfs user,noauto,file_mode=600,dir_mode=700 0 1" >> /etc/fstab
mount /dfs

# install python3
#yum -y install python34
# for some reason cc7 does not include python3, so we will have to build
# it from source. First install the dev tools
yum -y install wget
yum -y groupinstall "Development tools"
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
#Then download build and isntall python3
wget https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
tar xf Python-3.4.3.tgz
cd Python-3.4.3
./configure --prefix=/usr --enable-shared
make
make install

#run charm_shift_tool and auto screenshot tool
yum -y install libffi-devel
# install python3-virtualenv
pip3 install virtualenv

# Create a new charmshift user
#groupadd --system charmshiftgroup 
#useradd --system --gid charmshiftgroup --shell /bin/bash --home /home/charmshift charmshift
cp /etc/skel/.bash_profile /home/charmshift
cp /etc/skel/.bashrc /home/charmshift

#
## log into charmshift user
#su charmshift
#
## create python3 virtualenv and install all dependencies
#mkdir /home/charmshift
cd /home/charmshift
pyvenv-3.4 .
source bin/activate

pip3 install numpy
pip3 install pandas
pip3 install python-dateutil
pip3 install gspread
pip3 install oauth2client
pip3 install PyOpenSSL

# download repository from github
git clone https://github.com/einoj/charm_shift_tool.git

#run charm_shift_tool and auto screenshot tool

