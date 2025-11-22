# 📦 Guia de Instalação no Portainer

Guia passo a passo para instalar o Bot Telegram IPTV Tester no Portainer.

## ✅ Pré-requisitos

- Portainer instalado e funcionando
- Credenciais do Telegram (API_ID e API_HASH)
- Docker disponível no seu servidor/host

## 🚀 Método 1: Via Stack (Docker Compose) - RECOMENDADO

Este é o método mais fácil e recomendado.

### Passo 1: Acessar Portainer

1. Abra seu Portainer em `http://seu-servidor:9000`
2. Selecione seu **Environment**

### Passo 2: Criar Nova Stack

1. Vá para **Stacks** no menu lateral
2. Clique em **Add Stack**

### Passo 3: Configurar Stack

1. Em **Name**, digite: `telegram-iptv-bot`

2. Em **Build method**, selecione **Docker Compose**

3. Em **Editor**, copie e cole:

```yaml
version: '3.8'

services:
  telegram-iptv-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: telegram-iptv-bot
    restart: unless-stopped
    environment:
      API_ID: ${API_ID}
      API_HASH: ${API_HASH}
      CANAL_ORIGEM: ${CANAL_ORIGEM}
      TESTAR_AUTOMATICO: ${TESTAR_AUTOMATICO:-true}
      PALAVRAS_CHAVE: ${PALAVRAS_CHAVE}
      PALAVRAS_BLOQUEADAS: ${PALAVRAS_BLOQUEADAS}
      SUBSTITUICOES: ${SUBSTITUICOES}
      IPTV_TIMEOUT: ${IPTV_TIMEOUT:-15}
      WEBHOOK_URL: ${WEBHOOK_URL}
      WEBHOOK_TIMEOUT: ${WEBHOOK_TIMEOUT:-30}
    
    volumes:
      - telegram_iptv_data:/app/data
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    labels:
      - "com.example.description=Bot Telegram para testar e monitorar listas IPTV"
      - "com.example.version=1.0"

volumes:
  telegram_iptv_data:
    driver: local
```

### Passo 4: Adicionar Variáveis de Ambiente

Na seção **Environment variables**, clique em **Add environment variable** para cada uma:

```
API_ID = 123456789
API_HASH = abcdefghijklmnopqrstuvwxyz1234567890
CANAL_ORIGEM = meu_canal, outro_canal
TESTAR_AUTOMATICO = true
WEBHOOK_URL = (deixe vazio se não usar N8N)
```

**Exemplos de valores:**

| Variável | Exemplo |
|----------|---------|
| `API_ID` | `123456789` |
| `API_HASH` | `0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p` |
| `CANAL_ORIGEM` | `meu_canal` ou `123456789,-987654321` |
| `TESTAR_AUTOMATICO` | `true` |
| `WEBHOOK_URL` | `https://seu-webhook.com/webhook` |

### Passo 5: Deploy

1. Clique em **Deploy the stack**
2. Aguarde o build e inicialização (pode levar 2-3 minutos)

## 🔧 Método 2: Container Direto

Se preferir usar container individual:

### Passo 1: Ir para Containers

1. Clique em **Containers**
2. Clique em **Add Container**

### Passo 2: Configurar Container

**Basic settings:**
- **Name**: `telegram-iptv-bot`
- **Image**: `python:3.11-slim` (ou build manualmente)
- **Restart policy**: `Unless stopped`

**Env (Abra a seção Environment):**

```
API_ID=123456789
API_HASH=abcdefghijklmnopqrstuvwxyz1234567890
CANAL_ORIGEM=meu_canal
TESTAR_AUTOMATICO=true
IPTV_TIMEOUT=15
WEBHOOK_URL=
WEBHOOK_TIMEOUT=30
```

**Volumes:**
- Clique em **Add volume**
- **Container**: `/app/data`
- **Volume**: `telegram_iptv_data`

### Passo 3: Deploy

Clique em **Deploy the container**

## 📊 Monitorar o Bot

### Ver Logs

1. Vá para **Containers**
2. Clique em `telegram-iptv-bot`
3. Abra a aba **Logs**

Ou no terminal:
```bash
docker logs -f telegram-iptv-bot
```

### Acessar Dados

1. Vá para **Volumes**
2. Clique em `telegram_iptv_data`
3. Visualize os arquivos

## 🐛 Troubleshooting

### Stack não inicia

**Problema**: Stack fica em estado `deployerror`

**Solução**:
1. Verifique os logs: Clique no stack → **View logs**
2. Verifique variáveis de ambiente (especialmente `API_ID` e `API_HASH`)
3. Recrie a stack

### Container morre logo após iniciar

**Problema**: Estado `Exited`

**Solução**:
1. Verifique logs
2. Confirme que `CANAL_ORIGEM` está configurado
3. Verifique credenciais Telegram

### Arquivo CSV não aparece

**Problema**: Dados não são salvos

**Solução**:
1. Verifique se o volume está montado
2. Entre no container: `docker exec -it telegram-iptv-bot bash`
3. Verifique pasta: `ls -la /app/data/`

### Bot não conecta ao Telegram

**Problema**: Erro de autenticação

**Solução**:
1. Obtenha credenciais corretas em https://my.telegram.org/apps
2. Copie exatamente `API_ID` e `API_HASH`
3. Verifique se não há espaços extras

## 📈 Melhorias Recomendadas

### 1. Ativar Reverse Proxy

Se quiser acessar dados via web:

1. Configure Nginx/Traefik como reverse proxy
2. Configure credenciais de acesso

### 2. Alertas

Configure notificações para:
- Falhas do container
- Uso alto de disco

### 3. Backup

Crie backups regulares do volume:
```bash
docker run --rm -v telegram_iptv_data:/data -v $(pwd):/backup \
  busybox tar czf /backup/telegram_iptv_backup.tar.gz -C /data .
```

## 🔄 Atualizações

### Atualizar Stack

1. Modifique o docker-compose.yml
2. Clique em **Update the stack**
3. Configure pull image: **Always pull**

### Reconstruir Imagem

```bash
# No terminal do host
docker build -t telegram-iptv-bot .

# Recreate stack no Portainer
```

## 🛑 Remover Stack

1. Vá para **Stacks**
2. Clique em `telegram-iptv-bot`
3. Clique em **Remove**
4. Selecione **Remove volumes** se quiser deletar dados

## 📝 Exemplo de Configuração Completa

### Para ambiente de teste:

```
API_ID: 123456789
API_HASH: abcdefghijklmnopqrstuvwxyz1234567890
CANAL_ORIGEM: meu_canal_teste
TESTAR_AUTOMATICO: true
PALAVRAS_CHAVE: iptv,lista,m3u
PALAVRAS_BLOQUEADAS: teste,spam
IPTV_TIMEOUT: 10
WEBHOOK_URL: (vazio)
```

### Para ambiente de produção:

```
API_ID: 123456789
API_HASH: abcdefghijklmnopqrstuvwxyz1234567890
CANAL_ORIGEM: canal_producao_1, canal_producao_2
TESTAR_AUTOMATICO: true
PALAVRAS_CHAVE: (vazio - processa todas)
PALAVRAS_BLOQUEADAS: (vazio)
IPTV_TIMEOUT: 15
WEBHOOK_URL: https://seu-n8n.com/webhook/iptv
WEBHOOK_TIMEOUT: 30
```

---

**💡 Dica**: Depois de configurar, copie as variáveis de ambiente em um local seguro para possíveis reinstalações.
