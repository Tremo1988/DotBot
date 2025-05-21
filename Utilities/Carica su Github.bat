@echo off
REM ————————————————
REM git-auto-push.bat
REM ————————————————

REM 1) Trova il branch corrente
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"

REM 2) Costruisci un timestamp YYYY-MM-DD_HH-MM-SS
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set "TS=%%i"

REM 3) Esegui add/commit/push
git add -A
git commit -m "Auto commit %TS%"
git push origin %BRANCH%

REM Fine
