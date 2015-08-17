@echo off
set install_location=%1
if not exist %install_location% (
    echo 'Please specify a valid install path as an argument'
    exit /B
)

::copy cgi-bin\* %install_location%\cgi-bin 
::copy admin\* %install_location%\admin

ls %install_location%\admin
