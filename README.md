# 🤖 Bot Telegram IPTV Tester - Docker

Bot Telegram que monitora canais, detecta e testa automaticamente listas IPTV, salvando dados em CSV. Containerizado com Docker e pronto para instalação via **Portainer**.

## 📋 Características

- ✅ Monitora múltiplos canais do Telegram
- ✅ Detecta automaticamente links M3U em mensagens
- ✅ Testa listas IPTV (Xtream Codes)
- ✅ Extrai credenciais e informações da conta
- ✅ Salva dados em CSV
- ✅ **Envia listas extraídas para webhook N8N em tempo real** 🔗
- ✅ Envia notificações com detalhes das listas testadas
- ✅ Filtro de palavras-chave e palavras bloqueadas
- ✅ Persistência de dados
- ✅ Logs estruturados
- ✅ Containerizado e pronto para produção

## 🔑 Obter Credenciais Telegram

### API_ID e API_HASH
1. Acesse https://my.telegram.org/apps
2. Faça login com sua conta Telegram
3. Clique em "Create new application"
4. Preencha os dados solicitados
5. Copie **API ID** e **API Hash**

### Bot Token (Recomendado para Produção)
1. Abra o Telegram e procure por **@BotFather**
2. Envie `/newbot`
3. Escolha um nome e username para seu bot
4. Copie o **token** fornecido (formato: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. Adicione seu bot aos canais que deseja monitorar

**Vantagens do Bot Token**:
- ✅ Autenticação automática (sem interação)
- ✅ Funciona em ambientes containerizados
- ✅ Mais seguro (não requer código de verificação)
- ✅ Ideal para produção no Portainer

---

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

# Autenticação: Use BOT_TOKEN para automático (recomendado para produção)
# Obtenha em: https://t.me/BotFather
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Canais para monitorar
CANAL_ORIGEM=meu_canal, outro_canal

# Webhook N8N
WEBHOOK_URL=https://n8n.conekta.tech/webhook/whebhook1
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
| `BOT_TOKEN` | ❌ Não* | - | Token do bot para autenticação (obtém automaticamente) |
| `CANAL_ORIGEM` | ✅ Sim | - | Canais a monitorar (separados por vírgula) |
| `TESTAR_AUTOMATICO` | ❌ Não | `true` | Testar links M3U automaticamente |
| `PALAVRAS_CHAVE` | ❌ Não | - | Palavras para filtrar (separadas por vírgula) |
| `PALAVRAS_BLOQUEADAS` | ❌ Não | - | Palavras para bloquear (separadas por vírgula) |
| `SUBSTITUICOES` | ❌ Não | - | Substituições (formato: `orig1:novo1, orig2:novo2`) |
| `IPTV_TIMEOUT` | ❌ Não | `15` | Timeout para testes IPTV (segundos) |
| `WEBHOOK_URL` | ❌ Não | - | URL webhook N8N para notificações |
| `WEBHOOK_TIMEOUT` | ❌ Não | `30` | Timeout para webhook (segundos) |

**\*Bot Token**: Se configurado, o bot usa autenticação automática (sem interação). Se não definido, pode usar autenticação por telefone (apenas para desenvolvimento local).

## 📂 Estrutura de Arquivos

```
Testador-Docker/
├── Dockerfile              # Imagem Docker
├── docker-compose.yml      # Configuração Docker Compose
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de variáveis
├── .dockerignore          # Arquivos ignorados na build
├── telegram_iptv_bot.py   # Aplicação principal
├── manage.sh/bat          # Scripts de gerenciamento
├── build.sh/bat           # Scripts de build
├── README.md              # Este arquivo
├── INSTALACAO_PORTAINER.md # Guia Portainer
├── CONFIGURACOES_AVANCADAS.md # Configurações avançadas
└── RESUMO.md              # Resumo executivo
```

## 🔗 Integração com Webhook N8N

A aplicação **envia automaticamente** para seu webhook N8N sempre que:

1. **Uma lista IPTV é extraída** do Telegram
2. **Um documento M3U é recebido** no canal
3. **Uma lista é testada com sucesso** (com credenciais válidas)

### Dados Enviados para Webhook

```json
{
  "timestamp": "2025-11-22T14:30:45.123456",
  "tipo": "lista_iptv_extraida",
  "arquivo": "lista_20251122_143045.m3u",
  "canal_origem": "listasextrator",
  "conteudo": "# M3U da lista...",
  "total_canais": 245,
  "servidor": "example.com",
  "porta": 8080,
  "username": "usuario123",
  "password": "senha123",
  "status": "active",
  "data_vencimento": "2025-12-31"
}
```

### Configurar Webhook

No arquivo `.env`:

```env
# URL do seu webhook N8N
WEBHOOK_URL=https://n8n.conekta.tech/webhook/whebhook1

# Timeout para requisições (segundos)
WEBHOOK_TIMEOUT=30
```

### Exemplo: Receber no N8N

1. Crie um webhook trigger no N8N
2. Configure a URL
3. A aplicação Docker enviará POST automáticamente
4. Você pode processar os dados (salvar BD, enviar email, etc)

## 📂 Estrutura de Dados Persistentes

Os dados do bot são salvos em `/app/data`:

```
/app/data/
├── lists/                  # Listas M3U extraídas
│   ├── lista_20251122_143045.m3u
│   └── lista_20251122_150000.m3u
├── listas_iptv_validas.csv # Registro de todas as listas testadas
├── session_iptv_bot        # Sessão Telethon (autenticação)
├── bot.log                 # Logs de execução
└── sessions/               # Outras sessões
```

Com Docker Compose, estes dados são salvos em um named volume `telegram_iptv_data`.

## 🔍 Consultar Dados

Para acessar os arquivos gerados e verificar o envio para webhook:

```bash
# Ver logs (incluindo envios para webhook)
docker logs -f telegram-iptv-bot

# Copiar listas extraídas do container
docker cp telegram-iptv-bot:/app/data/lists/ ./

# Acessar dentro do container
docker exec -it telegram-iptv-bot bash
ls -la /app/data/lists/
cat /app/data/bot.log | grep webhook
```

### Monitorar Envios para Webhook

No arquivo de logs, procure por mensagens como:

```
✅ Enviado para webhook: lista_20251122_143045.m3u
❌ Erro webhook (500): Internal Server Error
⏱️ Timeout ao enviar para webhook (>30s)
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

### Listas não são extraídas
- Verifique se mensagens chegam ao canal configurado
- Confirme permissões do bot no canal
- Veja logs: `docker logs telegram-iptv-bot`

### Webhook não recebe dados
- Verifique se `WEBHOOK_URL` está correto
- Teste a URL manualmente: `curl -X POST https://seu-webhook.com -d '{"test":true}'`
- Verifique firewall/acesso de rede
- Aumente `WEBHOOK_TIMEOUT` se a resposta é lenta

### Falta permissão para salvar arquivos
- Verifique permissões do volume Docker
- Recrie volume: `docker volume rm telegram_iptv_data`

### Logs mostram "Timeout ao enviar webhook"
- Seu webhook está respondendo lentamente
- Aumente `WEBHOOK_TIMEOUT` (padrão: 30s)
- Verifique saúde do seu endpoint N8N

## 📞 Suporte

Para issues e sugestões, entre em contato via Telegram.

## 🔄 Fluxo de Funcionamento

```
Canal Telegram
      ↓
   Bot recebe mensagem/arquivo
      ↓
   Processa lista M3U
      ↓
   Salva em /app/data/lists/
      ↓
   POST → Webhook N8N
      ↓
   N8N processa dados
   (salva BD, envia email, etc)
```

## 📄 Licença

Este projeto é fornecido como está.

---

**Desenvolvido para extrair e monitorar listas IPTV via Telegram Bot com integração N8N** 🚀
