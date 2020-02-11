@echo off
cd ../
venv\Scripts\python.exe packager/setup.py build_apps
C:\Python36-32\python.exe packager/setup.py build_apps
rm -r packager/__whl_cache__
pause