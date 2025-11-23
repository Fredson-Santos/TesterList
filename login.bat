@echo off
REM Script para fazer login no Telegram interativamente

setlocal enabledelayedexpansion

set CONTAINER_NAME=telegram-iptv-bot

echo ========================================
echo Login Telegram - Bot IPTV
echo ========================================
echo.

REM Verificar se container existe
docker ps -a | findstr %CONTAINER_NAME% > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Container '%CONTAINER_NAME%' nao encontrado
    echo Inicie o container primeiro: docker-compose up -d
    exit /b 1
)

REM Parar container se estiver rodando
docker ps | findstr %CONTAINER_NAME% > nul 2>&1
if not errorlevel 1 (
    echo Parando container...
    docker stop %CONTAINER_NAME%
    timeout /t 2 /nobreak
)

REM Entrar no container de forma interativa
echo.
echo [INFO] Entre no shell do container:
echo.
echo Execute: python telegram_iptv_bot.py
echo Digite seu numero de telefone ou bot token
echo Confirme o codigo via SMS/Telegram
echo.

docker exec -it %CONTAINER_NAME% bash

echo.
echo Reiniciando container...
docker start %CONTAINER_NAME%

echo [OK] Container reiniciado
echo Ver logs: docker logs -f %CONTAINER_NAME%

pause
