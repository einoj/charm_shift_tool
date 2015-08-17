@echo off
set install_location=%1
::copy cgi-bin\* \\cern.ch\dfs\Websites\t\test-charmShiftTool\admin\
::copy admin\* \\cern.ch\dfs\Websites\t\test-charmShiftTool\admin\
if not exist %install_location% (
    echo 'derp'
    exit -1
)
    echo 'herp'
