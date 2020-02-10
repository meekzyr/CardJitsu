@echo off
cd ../
venv\Scripts\python.exe packager/setup.py build_apps
rm -r packager/__whl_cache__
pause