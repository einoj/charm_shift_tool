# This script will install the charm_shift_tool to a CERN
# openstack server. It is assumed that the server 
# is using a CC7 Extra x86_64# image

# Update all programs then install git
yum update
yum install git

#install python3
# Create a new charmshift user
