@echo off
REM Query myproxy captured requests

cd /d "%~dp0"

python main.py query %*