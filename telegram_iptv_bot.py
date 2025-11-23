#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram: Extrai listas IPTV e envia para webhook N8N
"""

import os
import asyncio
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv
from datetime import datetime
import json
import aiohttp
from pathlib import Path

# Carregar variáveis do .env
load_dotenv()

# Diretórios
DATA_DIR = Path('/app/data')
SESSIONS_DIR = DATA_DIR / 'sessions'
LISTS_DIR = DATA_DIR / 'lists'

# Criar diretórios se não existirem
DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
LISTS_DIR.mkdir(parents=True, exist_ok=True)

# Configurar logging
log_file = DATA_DIR / 'bot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
try:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    CANAL_ORIGEM = os.getenv('CANAL_ORIGEM')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', '30'))
    
    if not all([API_ID, API_HASH, CANAL_ORIGEM]):
        raise ValueError('API_ID, API_HASH e CANAL_ORIGEM são obrigatórios')
    
except Exception as e:
    logger.error(f'❌ Erro de configuração: {e}')
    exit(1)

# Cliente Telegram
client = TelegramClient(str(SESSIONS_DIR / 'bot_session'), API_ID, API_HASH)


async def enviar_webhook(nome_arquivo, conteudo):
    """Envia lista para webhook N8N"""
    if not WEBHOOK_URL:
        return False
    
    try:
        payload = {
            'timestamp': datetime.now().isoformat(),
            'arquivo': nome_arquivo,
            'conteudo': conteudo,
            'canal_origem': CANAL_ORIGEM
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                WEBHOOK_URL,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=WEBHOOK_TIMEOUT)
            ) as response:
                if response.status == 200:
                    logger.info(f'✅ Webhook enviado: {nome_arquivo}')
                    return True
                else:
                    logger.error(f'❌ Webhook falhou ({response.status})')
                    return False
    except Exception as e:
        logger.error(f'❌ Erro ao enviar webhook: {e}')
        return False


async def processar_mensagem(message):
    """Processa mensagens do canal"""
    try:
        # Mensagens de texto
        if message.text:
            conteudo = message.text
            
            # Detecta listas M3U ou URLs
            if conteudo.strip().startswith('#EXTM3U') or 'http' in conteudo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f'lista_{timestamp}.m3u'
                caminho = LISTS_DIR / nome_arquivo
                
                # Salva arquivo
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                
                logger.info(f'💾 Arquivo salvo: {nome_arquivo}')
                
                # Envia para webhook
                await enviar_webhook(nome_arquivo, conteudo)
        
        # Documentos (M3U, TXT)
        if message.document:
            arquivo = await client.download_media(message.document, file=str(LISTS_DIR))
            if arquivo:
                nome_arquivo = os.path.basename(arquivo)
                logger.info(f'📥 Arquivo baixado: {nome_arquivo}')
                
                # Lê e envia
                with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read()
                
                await enviar_webhook(nome_arquivo, conteudo)
    
    except Exception as e:
        logger.error(f'❌ Erro ao processar: {e}')


@client.on(events.NewMessage(chats=CANAL_ORIGEM))
async def handler(event):
    """Handler para novas mensagens"""
    await processar_mensagem(event.message)


async def main():
    """Inicia o bot"""
    await client.start()
    logger.info(f'🚀 Bot iniciado')
    logger.info(f'📢 Canal: {CANAL_ORIGEM}')
    logger.info(f'🔗 Webhook: {WEBHOOK_URL if WEBHOOK_URL else "Não configurado"}')
    logger.info(f'💾 Dados: {LISTS_DIR}')
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('⏹️ Bot parado')
    except Exception as e:
        logger.error(f'❌ Erro fatal: {e}')
        exit(1)
