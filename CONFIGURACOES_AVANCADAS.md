# Configurações Avançadas - Bot Telegram IPTV Docker

## 🔒 Segurança em Produção

### 1. Usar Secrets do Docker Swarm

Se estiver usando Docker Swarm:

```bash
echo "seu_api_hash_aqui" | docker secret create api_hash -
echo "123456789" | docker secret create api_id -
```

Docker Compose adaptado:
```yaml
secrets:
  api_id:
    external: true
  api_hash:
    external: true

services:
  telegram-iptv-bot:
    secrets:
      - api_id
      - api_hash
```

### 2. Usar .env com permissões restritivas

```bash
# Criar arquivo com permissões restritas
touch .env
chmod 600 .env
# Editar arquivo com nano/vim
```

### 3. Registry Privado

```bash
# Login em registry privado
docker login seu-registry.com

# Taggear imagem
docker tag telegram-iptv-bot:latest seu-registry.com/telegram-iptv-bot:latest

# Push
docker push seu-registry.com/telegram-iptv-bot:latest
```

## 📈 Performance

### 1. Limitar Recursos

```yaml
services:
  telegram-iptv-bot:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 2. Aumentar Timeout para Redes Lentas

```env
IPTV_TIMEOUT=30
WEBHOOK_TIMEOUT=60
```

### 3. Usar Cache em Build

```dockerfile
# Bom - cache usado
FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY telegram_iptv_bot.py .
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
      
      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v2
        with:
          context: ./Testador-Docker
          push: true
          tags: seu-usuario/telegram-iptv-bot:latest
```

## 🔍 Monitoramento

### 1. Adicionar Prometheus

```yaml
services:
  telegram-iptv-bot:
    environment:
      - PYTHONUNBUFFERED=1
    labels:
      - "prometheus-job=telegram-iptv-bot"
```

### 2. Logs Centralizados (ELK Stack)

```yaml
services:
  telegram-iptv-bot:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=telegram-iptv-bot"
```

### 3. Health Check

```yaml
services:
  telegram-iptv-bot:
    healthcheck:
      test: ["CMD", "test", "-f", "/app/data/bot.log"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 🌐 Rede

### 1. Custom Network

```yaml
networks:
  telegram:
    driver: bridge

services:
  telegram-iptv-bot:
    networks:
      - telegram
```

### 2. Variáveis de Rede

```yaml
services:
  telegram-iptv-bot:
    environment:
      - PROXY_URL=${PROXY_URL}
      - DNS_SERVER=${DNS_SERVER}
```

## 💾 Backup e Restore

### Backup

```bash
#!/bin/bash
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

docker run --rm \
  -v telegram_iptv_data:/data \
  -v "$BACKUP_DIR":/backup \
  busybox tar czf /backup/backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### Restore

```bash
BACKUP_FILE="backup_20250101_120000.tar.gz"

docker run --rm \
  -v telegram_iptv_data:/data \
  -v ./backups:/backup \
  busybox tar xzf /backup/$BACKUP_FILE -C /data
```

## 🚀 Escalabilidade

### 1. Múltiplas Instâncias

```yaml
version: '3.8'

services:
  telegram-iptv-bot-1:
    # Monitorar canal 1
    environment:
      - CANAL_ORIGEM=canal_1
  
  telegram-iptv-bot-2:
    # Monitorar canal 2
    environment:
      - CANAL_ORIGEM=canal_2
```

### 2. Load Balancer (Nginx)

```nginx
upstream telegram_bot {
    server telegram-iptv-bot:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://telegram_bot;
    }
}
```

## 📊 Analytics

### Enviar métricas para N8N

```python
# Adicionar ao telegram_iptv_bot.py
import json
import requests

def send_metrics(metrics):
    webhook_url = os.getenv('METRICS_WEBHOOK_URL')
    requests.post(webhook_url, json=metrics)
```

## 🔧 Troubleshooting Avançado

### 1. Debug Mode

```yaml
environment:
  - DEBUG=true
  - LOG_LEVEL=DEBUG
```

### 2. Profiling

```bash
docker exec telegram-iptv-bot python -m cProfile telegram_iptv_bot.py
```

### 3. Network Issues

```bash
# Teste de conectividade
docker exec telegram-iptv-bot wget -q -O- https://api.telegram.org

# Ver conexões ativas
docker exec telegram-iptv-bot netstat -an | grep ESTABLISHED
```

## 🎯 Otimizações

### 1. Multi-stage Build (Dockerfile otimizado)

```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY telegram_iptv_bot.py .

ENV PATH=/root/.local/bin:$PATH
CMD ["python", "telegram_iptv_bot.py"]
```

### 2. Cache Volume

```yaml
volumes:
  pip_cache:
    driver: local

services:
  telegram-iptv-bot:
    volumes:
      - pip_cache:/root/.cache/pip
```

### 3. Reduce Image Size

```bash
# Ver tamanho
docker images telegram-iptv-bot

# Otimizar
docker build --no-cache -t telegram-iptv-bot .
```

## 📝 Documentação Interna

### Adicionar labels

```yaml
labels:
  com.example.version: "1.0"
  com.example.maintainer: "seu-email@exemplo.com"
  com.example.description: "Bot Telegram para testar IPTV"
  com.example.documentation: "https://seu-repo/README.md"
```

## 🔐 Renovação de Credenciais

### Script de rotação de secrets

```bash
#!/bin/bash

# Backup credenciais antigas
cp .env .env.backup.$(date +%Y%m%d)

# Gerar novas credenciais (manual)
echo "Gerar novas credenciais em: https://my.telegram.org/apps"
read -p "Novo API_ID: " NEW_API_ID
read -p "Novo API_HASH: " NEW_API_HASH

# Atualizar .env
sed -i "s/^API_ID=.*/API_ID=$NEW_API_ID/" .env
sed -i "s/^API_HASH=.*/API_HASH=$NEW_API_HASH/" .env

# Reiniciar container
docker-compose restart

echo "Credenciais renovadas e container reiniciado!"
```

---

**Dica**: Para mais informações sobre Docker, consulte: https://docs.docker.com/
