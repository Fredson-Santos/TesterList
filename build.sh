#!/bin/bash
# Script para construir e publicar imagem Docker

set -e

IMAGE_NAME="telegram-iptv-bot"
TAG="latest"
REGISTRY="" # Deixe vazio para usar Docker Hub, ou configure seu registry

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Build Docker - Telegram IPTV Bot${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 1. Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado. Instale Docker primeiro.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker encontrado${NC}\n"

# 2. Construir imagem
echo -e "${BLUE}🔨 Construindo imagem Docker...${NC}"
docker build -t ${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagem construída com sucesso!${NC}\n"
else
    echo -e "${RED}❌ Erro ao construir imagem${NC}"
    exit 1
fi

# 3. Mostrar informações da imagem
echo -e "${BLUE}📊 Informações da imagem:${NC}"
docker images | grep ${IMAGE_NAME} | head -1

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Build completo!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${BLUE}Próximos passos:${NC}"
echo -e "1. Execute com Docker Compose:"
echo -e "   ${GREEN}docker-compose up -d${NC}"
echo ""
echo -e "2. Ou execute manualmente:"
echo -e "   ${GREEN}docker run -d \\${NC}"
echo -e "   ${GREEN}  --name telegram-iptv-bot \\${NC}"
echo -e "   ${GREEN}  --restart unless-stopped \\${NC}"
echo -e "   ${GREEN}  --env-file .env \\${NC}"
echo -e "   ${GREEN}  -v telegram_iptv_data:/app/data \\${NC}"
echo -e "   ${GREEN}  ${IMAGE_NAME}:${TAG}${NC}"
echo ""
echo -e "3. Verifique logs:"
echo -e "   ${GREEN}docker logs -f telegram-iptv-bot${NC}"
echo ""

# 4. Se configurado registry, fazer push (opcional)
if [ ! -z "$REGISTRY" ]; then
    echo -e "${BLUE}📤 Enviando para registry...${NC}"
    docker tag ${IMAGE_NAME}:${TAG} ${REGISTRY}/${IMAGE_NAME}:${TAG}
    docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}
    echo -e "${GREEN}✓ Imagem enviada para registry!${NC}"
fi
