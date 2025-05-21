@echo off
cd /d %~dp0\..
call venv\Scripts\activate
python modules\Controllo_bilancio.py
pause
