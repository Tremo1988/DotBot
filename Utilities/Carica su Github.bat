@echo off
SET /P commit_msg="Inserisci il messaggio del commit: "

echo.
echo ► Aggiunta file modificati...
git add .

echo.
echo ► Commit in corso...
git commit -m "%commit_msg%"

echo.
echo ► Push su GitHub...
git push origin advanced/step-1

echo.
echo ► Operazione completata. Premi un tasto per uscire.
pause >nul
