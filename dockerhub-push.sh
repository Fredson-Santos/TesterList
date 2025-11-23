#!/bin/bash
# Script para fazer build e push para Docker Hub

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Docker Hub - Build e Push${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Configurações
DOCKER_USERNAME="${1}"
IMAGE_NAME="telegram-iptv-bot"
TAG="${2:-latest}"

# Se não informar usuário
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${YELLOW}Uso: ./dockerhub-push.sh <seu-usuario-dockerhub> [tag]${NC}"
    echo ""
    echo "Exemplos:"
    echo "  ./dockerhub-push.sh fred"
    echo "  ./dockerhub-push.sh fred v1.0"
    echo ""
    exit 1
fi

REGISTRY="${DOCKER_USERNAME}/${IMAGE_NAME}"

echo -e "${BLUE}Configuração:${NC}"
echo "  Usuário Docker Hub: ${DOCKER_USERNAME}"
echo "  Imagem: ${REGISTRY}"
echo "  Tag: ${TAG}"
echo ""

# Verificar Docker
echo -e "${BLUE}🐳 Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker OK${NC}"

# Fazer login
echo -e "\n${BLUE}🔐 Fazendo login no Docker Hub...${NC}"
docker login -u "$DOCKER_USERNAME"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha no login${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Login OK${NC}"

# Build da imagem
echo -e "\n${BLUE}🔨 Construindo imagem...${NC}"
docker build -t ${REGISTRY}:${TAG} -t ${REGISTRY}:latest .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha ao construir imagem${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Imagem construída${NC}"

# Push para Docker Hub
echo -e "\n${BLUE}📤 Enviando para Docker Hub (${TAG})...${NC}"
docker push ${REGISTRY}:${TAG}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha ao fazer push${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Tag ${TAG} enviada${NC}"

# Push latest se não for latest
if [ "$TAG" != "latest" ]; then
    echo -e "\n${BLUE}📤 Enviando tag latest...${NC}"
    docker push ${REGISTRY}:latest
    echo -e "${GREEN}✓ Tag latest enviada${NC}"
fi

# Informações da imagem
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Push concluído com sucesso!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${BLUE}Imagem disponível em:${NC}"
echo -e "${GREEN}  https://hub.docker.com/r/${REGISTRY}${NC}"
echo ""
echo -e "${BLUE}Para usar em outro servidor:${NC}"
echo -e "  ${GREEN}docker pull ${REGISTRY}:${TAG}${NC}"
echo -e "  ${GREEN}docker run -d --name telegram-iptv-bot \\${NC}"
echo -e "  ${GREEN}  --env-file .env \\${NC}"
echo -e "  ${GREEN}  -v telegram_iptv_data:/app/data \\${NC}"
echo -e "  ${GREEN}  ${REGISTRY}:${TAG}${NC}"
echo ""

# Ver informações
echo -e "${BLUE}Informações da imagem local:${NC}"
docker images | grep ${REGISTRY} | head -5
