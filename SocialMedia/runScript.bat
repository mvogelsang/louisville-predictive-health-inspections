@ECHO off

set "script_path=%~dp0"
set "script_path=%script_path%CSVtoJSON.py"

python %script_path% %*

exit 0