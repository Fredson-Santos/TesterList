#!/bin/bash
# Script para fazer login no Telegram interativamente

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Login Telegram - Bot IPTV${NC}"
echo -e "${BLUE}========================================${NC}\n"

CONTAINER_NAME="telegram-iptv-bot"

# Verificar se container existe
if ! docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}❌ Container '$CONTAINER_NAME' não encontrado${NC}"
    echo "Inicie o container primeiro: docker-compose up -d"
    exit 1
fi

# Parar container se estiver rodando
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${BLUE}Parando container...${NC}"
    docker stop "$CONTAINER_NAME"
    sleep 2
fi

# Entrar no container de forma interativa
echo -e "${BLUE}📱 Entre no shell do container:${NC}"
echo -e "  Execute: ${GREEN}python telegram_iptv_bot.py${NC}"
echo -e "  Digite seu número de telefone ou bot token${NC}"
echo -e "  Confirme o código via SMS/Telegram${NC}"
echo ""

docker exec -it "$CONTAINER_NAME" bash

echo ""
echo -e "${BLUE}Reiniciando container...${NC}"
docker start "$CONTAINER_NAME"

echo -e "${GREEN}✓ Container reiniciado${NC}"
echo -e "${BLUE}Ver logs: ${GREEN}docker logs -f $CONTAINER_NAME${NC}"
