@echo off
echo Iniciando servidor Flask...
echo.
echo Acesse a aplicacao em:
echo   - Votacao: http://localhost:5000
echo   - Admin:   http://localhost:5000/admin
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

cd /d "%~dp0"
.venv\Scripts\python.exe app.py

pause
