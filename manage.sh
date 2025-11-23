#!/bin/bash
# Script de gerenciamento do container

set -e

CONTAINER_NAME="telegram-iptv-bot"
IMAGE_NAME="telegram-iptv-bot"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detectar comando docker-compose (novo: docker compose vs antigo: docker-compose)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}❌ docker-compose não encontrado!${NC}"
    echo "Instale com: sudo apt-get install docker-compose"
    echo "Ou use a versão nova: sudo apt-get install docker.io"
    exit 1
fi

# Função para exibir ajuda
show_help() {
    echo -e "${BLUE}Gerenciamento do Bot Telegram IPTV${NC}"
    echo ""
    echo "Uso: ./manage.sh [comando]"
    echo ""
    echo "Comandos:"
    echo "  start      - Iniciar container"
    echo "  stop       - Parar container"
    echo "  restart    - Reiniciar container"
    echo "  logs       - Ver logs em tempo real"
    echo "  shell      - Acessar shell do container"
    echo "  status     - Ver status do container"
    echo "  build      - Construir imagem"
    echo "  clean      - Remover container e volumes"
    echo "  backup     - Fazer backup dos dados"
    echo ""
}

# Função para iniciar
start_container() {
    echo -e "${BLUE}Iniciando container...${NC}"
    $DOCKER_COMPOSE up -d
    echo -e "${GREEN}✓ Container iniciado!${NC}"
    sleep 2
    status_container
}

# Função para parar
stop_container() {
    echo -e "${BLUE}Parando container...${NC}"
    $DOCKER_COMPOSE down
    echo -e "${GREEN}✓ Container parado!${NC}"
}

# Função para reiniciar
restart_container() {
    echo -e "${BLUE}Reiniciando container...${NC}"
    $DOCKER_COMPOSE restart
    echo -e "${GREEN}✓ Container reiniciado!${NC}"
}

# Função para ver logs
show_logs() {
    echo -e "${BLUE}Logs do container (Ctrl+C para sair)${NC}"
    docker logs -f $CONTAINER_NAME
}

# Função para entrar no shell
enter_shell() {
    echo -e "${BLUE}Acessando shell do container...${NC}"
    docker exec -it $CONTAINER_NAME bash
}

# Função para ver status
status_container() {
    echo -e "${BLUE}Status do container:${NC}"
    docker ps -a | grep $CONTAINER_NAME || echo -e "${RED}Container não encontrado${NC}"
}

# Função para construir
build_image() {
    echo -e "${BLUE}Construindo imagem...${NC}"
    docker build -t $IMAGE_NAME .
    echo -e "${GREEN}✓ Imagem construída!${NC}"
}

# Função para limpar
clean() {
    echo -e "${YELLOW}Aviso: Isto irá remover o container e os dados!${NC}"
    read -p "Deseja continuar? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${BLUE}Removendo container...${NC}"
        $DOCKER_COMPOSE down -v
        echo -e "${GREEN}✓ Limpeza completa!${NC}"
    else
        echo "Cancelado."
    fi
}

# Função para backup
backup() {
    BACKUP_FILE="telegram_iptv_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    echo -e "${BLUE}Criando backup: $BACKUP_FILE${NC}"
    docker run --rm -v telegram_iptv_data:/data -v $(pwd):/backup \
        busybox tar czf /backup/$BACKUP_FILE -C /data .
    echo -e "${GREEN}✓ Backup criado: $BACKUP_FILE${NC}"
}

# Main
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    shell)
        enter_shell
        ;;
    status)
        status_container
        ;;
    build)
        build_image
        ;;
    clean)
        clean
        ;;
    backup)
        backup
        ;;
    *)
        echo -e "${RED}Comando desconhecido: $1${NC}"
        show_help
        exit 1
        ;;
esac
