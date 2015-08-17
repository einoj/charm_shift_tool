@echo off
set install_location=%1
if not exist %install_location% (
    echo 'Please specify a valid install path as an argument'
    exit /B
)

copy tool\* %install_location%
mkdir %install_location%\admin
copy admin\* %install_location%\admin\

