@echo off
REM Script de gerenciamento do container para Windows

setlocal enabledelayedexpansion

set CONTAINER_NAME=telegram-iptv-bot
set IMAGE_NAME=telegram-iptv-bot

if "%1"=="" (
    goto show_help
)

if /i "%1"=="start" (
    goto start_container
) else if /i "%1"=="stop" (
    goto stop_container
) else if /i "%1"=="restart" (
    goto restart_container
) else if /i "%1"=="logs" (
    goto show_logs
) else if /i "%1"=="shell" (
    goto enter_shell
) else if /i "%1"=="status" (
    goto status_container
) else if /i "%1"=="build" (
    goto build_image
) else if /i "%1"=="clean" (
    goto clean_container
) else (
    goto show_help
)

:show_help
echo Gerenciamento do Bot Telegram IPTV
echo.
echo Uso: manage.bat [comando]
echo.
echo Comandos:
echo   start    - Iniciar container
echo   stop     - Parar container
echo   restart  - Reiniciar container
echo   logs     - Ver logs em tempo real
echo   shell    - Acessar shell do container
echo   status   - Ver status do container
echo   build    - Construir imagem
echo   clean    - Remover container e volumes
echo.
exit /b 0

:start_container
echo [INFO] Iniciando container...
docker-compose up -d
echo [OK] Container iniciado!
timeout /t 2 /nobreak
docker ps -a | findstr %CONTAINER_NAME%
exit /b 0

:stop_container
echo [INFO] Parando container...
docker-compose down
echo [OK] Container parado!
exit /b 0

:restart_container
echo [INFO] Reiniciando container...
docker-compose restart
echo [OK] Container reiniciado!
exit /b 0

:show_logs
echo [INFO] Logs do container (Ctrl+C para sair)
docker logs -f %CONTAINER_NAME%
exit /b 0

:enter_shell
echo [INFO] Acessando shell do container...
docker exec -it %CONTAINER_NAME% bash
exit /b 0

:status_container
echo [INFO] Status do container:
docker ps -a | findstr %CONTAINER_NAME%
exit /b 0

:build_image
echo [INFO] Construindo imagem...
docker build -t %IMAGE_NAME% .
echo [OK] Imagem construida!
exit /b 0

:clean_container
echo [AVISO] Isto ira remover o container e os dados!
set /p confirm="Deseja continuar? (s/n): "
if /i "%confirm%"=="s" (
    echo [INFO] Removendo container...
    docker-compose down -v
    echo [OK] Limpeza completa!
) else (
    echo Cancelado.
)
exit /b 0
