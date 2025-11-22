@echo off
REM Script para construir e testar imagem Docker no Windows

setlocal enabledelayedexpansion

set IMAGE_NAME=telegram-iptv-bot
set TAG=latest

echo ========================================
echo Build Docker - Telegram IPTV Bot
echo ========================================
echo.

REM Verificar se Docker está instalado
docker --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker nao encontrado. Instale Docker primeiro.
    pause
    exit /b 1
)

echo [OK] Docker encontrado
echo.

REM Construir imagem
echo [INFO] Construindo imagem Docker...
docker build -t %IMAGE_NAME%:%TAG% .

if errorlevel 1 (
    echo [ERRO] Falha ao construir imagem
    pause
    exit /b 1
)

echo [OK] Imagem construida com sucesso!
echo.

REM Mostrar informações
echo [INFO] Informacoes da imagem:
docker images | findstr %IMAGE_NAME%

echo.
echo ========================================
echo [OK] Build completo!
echo ========================================
echo.

echo [INFO] Proximos passos:
echo.
echo 1. Configurar .env:
echo    copy .env.example .env
echo    (edite o arquivo com suas credenciais)
echo.
echo 2. Executar com Docker Compose:
echo    docker-compose up -d
echo.
echo 3. Verificar logs:
echo    docker logs -f telegram-iptv-bot
echo.

pause
