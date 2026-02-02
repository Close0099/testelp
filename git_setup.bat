@echo off
REM Script para enviar o projeto para GitHub

echo.
echo ======================================
echo   ENVIANDO PROJETO PARA GITHUB
echo ======================================
echo.

REM Inicializar repositório git
echo [1] Inicializando repositório git...
git init
git config user.name "Seu Nome"
git config user.email "seu.email@gmail.com"

REM Adicionar todos os arquivos
echo [2] Adicionando arquivos...
git add .

REM Fazer commit
echo [3] Fazendo commit...
git commit -m "Initial commit: Sistema de avaliação de satisfação full-stack"

REM Informar próximos passos
echo.
echo ======================================
echo   PRÓXIMOS PASSOS:
echo ======================================
echo.
echo 1. Acesse: https://github.com/new
echo 2. Nome do repositório: testelp (ou outro que preferir)
echo 3. NÃO selecione "Initialize this repository"
echo 4. Clique em "Create repository"
echo.
echo 5. Execute um destes comandos:
echo.
echo    git remote add origin https://github.com/SEU-USUARIO/testelp.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 6. Digite seu GitHub username e Personal Access Token quando pedido
echo.
echo ======================================
echo.

pause
