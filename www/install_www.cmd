@echo off
set install_location=g:\Websites\c\charmshifttool
if not exist %install_location% (
    echo 'Please specify a valid install path as an argument'
    exit /B
)

copy tool\* %install_location%
copy ..\database_ctrl.py %install_location%
mkdir %install_location%\admin
copy admin\* %install_location%\admin\
copy ..\database_ctrl.py %install_location%\admin\

