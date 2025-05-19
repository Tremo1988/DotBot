@echo off
cd /d C:\DotBot
call venv\Scripts\activate.bat
streamlit run modules/dashboard.py
pause
