# 🤖 Bot Telegram IPTV Tester - Docker

Bot Telegram que monitora canais, detecta e testa automaticamente listas IPTV, salvando dados em CSV. Containerizado com Docker e pronto para instalação via **Portainer**.

## 📋 Características

- ✅ Monitora múltiplos canais do Telegram
- ✅ Detecta automaticamente links M3U em mensagens
- ✅ Testa listas IPTV (Xtream Codes)
- ✅ Extrai credenciais e informações da conta
- ✅ Salva dados em CSV
- ✅ Envia notificações para webhook N8N (opcional)
- ✅ Filtro de palavras-chave e palavras bloqueadas
- ✅ Persistência de dados
- ✅ Logs estruturados
- ✅ Containerizado e pronto para produção

## 🐳 Instalação via Docker

### 1. Clonar ou copiar os arquivos

```bash
cd Testador-Docker
```

### 2. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
# Credenciais Telegram
API_ID=123456789
API_HASH=abcdefghijklmnopqrstuvwxyz1234567890

# Canais para monitorar
CANAL_ORIGEM=meu_canal, outro_canal
```

### 3. Construir imagem Docker

```bash
docker build -t telegram-iptv-bot .
```

### 4. Executar container

```bash
docker run -d \
  --name telegram-iptv-bot \
  --restart unless-stopped \
  --env-file .env \
  -v telegram_iptv_data:/app/data \
  telegram-iptv-bot
```

### 5. Verificar logs

```bash
docker logs -f telegram-iptv-bot
```

## 🔧 Instalação via Docker Compose

### 1. Configurar `.env`

```bash
cp .env.example .env
# Editar com suas credenciais
```

### 2. Iniciar serviço

```bash
docker-compose up -d
```

### 3. Parar serviço

```bash
docker-compose down
```

## 🎛️ Instalação via Portainer

### 1. Preparar arquivo `.env`

Você precisará das variáveis de ambiente definidas. Portainer usará a opção "Environment" para configurá-las.

### 2. No Portainer

1. Vá para **Containers** → **Add Container**
2. Defina:
   - **Image**: `telegram-iptv-bot:latest` (ou especifique repositório)
   - **Container name**: `telegram-iptv-bot`
   - **Restart policy**: `Unless stopped`

3. Em **Environment**:
   ```
   API_ID=123456789
   API_HASH=abcdefghijklmnopqrstuvwxyz1234567890
   CANAL_ORIGEM=meu_canal
   TESTAR_AUTOMATICO=true
   ```

4. Em **Volumes**:
   - Add volume mount: `/app/data` → `telegram_iptv_data` (named volume)

5. Clique em **Deploy the container**

### 3. Via Portainer Stack (docker-compose)

1. Vá para **Stacks** → **Add Stack**
2. Cole o conteúdo de `docker-compose.yml`
3. Adicione as variáveis de ambiente na seção **Environment**
4. Clique em **Deploy**

## 📝 Variáveis de Ambiente

| Variável | Obrigatório | Padrão | Descrição |
|----------|------------|--------|-----------|
| `API_ID` | ✅ Sim | - | ID da API Telegram (obtenha em https://my.telegram.org/apps) |
| `API_HASH` | ✅ Sim | - | Hash da API Telegram |
| `CANAL_ORIGEM` | ✅ Sim | - | Canais a monitorar (separados por vírgula) |
| `TESTAR_AUTOMATICO` | ❌ Não | `true` | Testar links M3U automaticamente |
| `PALAVRAS_CHAVE` | ❌ Não | - | Palavras para filtrar (separadas por vírgula) |
| `PALAVRAS_BLOQUEADAS` | ❌ Não | - | Palavras para bloquear (separadas por vírgula) |
| `SUBSTITUICOES` | ❌ Não | - | Substituições (formato: `orig1:novo1, orig2:novo2`) |
| `IPTV_TIMEOUT` | ❌ Não | `15` | Timeout para testes IPTV (segundos) |
| `WEBHOOK_URL` | ❌ Não | - | URL webhook N8N para notificações |
| `WEBHOOK_TIMEOUT` | ❌ Não | `30` | Timeout para webhook (segundos) |

## 📂 Estrutura de Arquivos

```
Testador-Docker/
├── Dockerfile              # Imagem Docker
├── docker-compose.yml      # Configuração Docker Compose
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de variáveis
├── .dockerignore          # Arquivos ignorados na build
├── telegram_iptv_bot.py   # Aplicação principal
└── README.md              # Este arquivo
```

## 📊 Dados Persistentes

Os dados do bot são salvos em `/app/data`:

- `listas_iptv_validas.csv` - Listas IPTV testadas e válidas
- `session_iptv_bot` - Sessão Telethon do bot
- `bot.log` - Logs de execução

Com Docker Compose, estes dados são salvos em um named volume `telegram_iptv_data`.

## 🔍 Consultar Dados

Para acessar os arquivos CSV gerados:

```bash
# Ver logs
docker logs telegram-iptv-bot

# Copiar CSV do container
docker cp telegram-iptv-bot:/app/data/listas_iptv_validas.csv ./

# Acessar dentro do container
docker exec -it telegram-iptv-bot bash
cat /app/data/listas_iptv_validas.csv
```

## 🧹 Limpeza

```bash
# Parar e remover container
docker stop telegram-iptv-bot
docker rm telegram-iptv-bot

# Remover imagem
docker rmi telegram-iptv-bot

# Remover volume de dados
docker volume rm telegram_iptv_data
```

## 🔐 Segurança

- ✅ Credenciais via variáveis de ambiente (não no código)
- ✅ Senhas mascaradas em logs
- ✅ Volume dedicado para dados sensíveis
- ✅ Restart automático apenas se necessário
- ✅ Limite de logs para evitar disco cheio

## 📝 Logs

Logs estão disponíveis em:
- Console: `docker logs -f telegram-iptv-bot`
- Arquivo: `/app/data/bot.log` (dentro do container)
- Portainer: Seção de logs do container

## 🔄 Atualizar Imagem

```bash
# Baixar última versão
docker pull telegram-iptv-bot:latest

# Parar e remover container antigo
docker stop telegram-iptv-bot
docker rm telegram-iptv-bot

# Executar novo container
docker run -d --name telegram-iptv-bot ... (ver seção "Executar container")
```

## 🆘 Troubleshooting

### Bot não conecta ao Telegram
- Verifique `API_ID` e `API_HASH` em `https://my.telegram.org/apps`
- Certifique-se que os canais em `CANAL_ORIGEM` existem

### CSV não é gerado
- Verifique se o volume `/app/data` está montado
- Verifique logs: `docker logs telegram-iptv-bot`

### Links M3U não são detectados
- Verifique se a mensagem é enviada para um dos canais configurados
- Confirme que `TESTAR_AUTOMATICO=true`

### Falta permissão para escrever no CSV
- Verifique permissões do volume Docker
- Recrie volume: `docker volume rm telegram_iptv_data`

## 📞 Suporte

Para issues e sugestões, entre em contato via Telegram.

## 📄 Licença

Este projeto é fornecido como está.

---

**Desenvolvido para teste e monitoramento de listas IPTV via Telegram Bot**
