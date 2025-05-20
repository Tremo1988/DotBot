@echo off
SET COMMIT_MESSAGE=Aggiornamento automatico

git add .
git commit -m "%COMMIT_MESSAGE%"
git push origin HEAD

echo.
echo Codice caricato con successo su GitHub!
pause
