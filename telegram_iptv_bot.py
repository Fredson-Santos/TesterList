#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram: Monitora canais e testa listas IPTV automaticamente
Detecta links M3U nas mensagens, testa e salva no CSV
"""

import os
import re
import asyncio
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv
import requests
import json
import time
import csv
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Carregar variáveis do .env
load_dotenv()

# Diretório de dados
DATA_DIR = os.getenv('DATA_DIR', '/app/data')
SESSIONS_DIR = os.path.join(DATA_DIR, 'sessions')
LISTS_DIR = os.path.join(DATA_DIR, 'lists')

for directory in [DATA_DIR, SESSIONS_DIR, LISTS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

# Configurar logging
log_file = os.path.join(DATA_DIR, 'bot.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Arquivo CSV para salvar listas válidas
CSV_FILE = os.path.join(DATA_DIR, 'listas_iptv_validas.csv')

# Cabeçalhos do CSV
CSV_HEADERS = ['link_m3u', 'servidor', 'porta', 'username', 'password', 'data_criacao', 'data_vencimento', 
               'total_canais', 'status', 'data_teste', 'observacoes', 'canal_origem', 'mensagem_id']


class WebhookSender:
    """Classe para enviar dados para webhook do n8n"""
    
    def __init__(self, webhook_url: str, timeout: int = 30):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Telegram-IPTV-Bot/1.0'
        })
    
    def send_iptv_data(self, data: Dict) -> bool:
        """
        Envia dados da lista IPTV para o webhook do n8n
        
        Args:
            data: Dicionário com dados da lista IPTV
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.webhook_url:
            return False
        
        try:
            response = self.session.post(
                self.webhook_url,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            print(f"[OK] Dados enviados para webhook: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Falha ao enviar para webhook: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"Resposta do servidor: {e.response.text}")
                except:
                    pass
            return False
        except Exception as e:
            print(f"[ERRO] Erro inesperado ao enviar webhook: {e}")
            return False


class XtreamCodesAPI:
    """Classe para consultar a API Xtream Codes"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_credentials(self, m3u_url: str) -> Optional[Dict]:
        """Extrai credenciais (servidor, porta, username, password) da URL M3U Xtream Codes"""
        try:
            parsed = urlparse(m3u_url)
            query_params = parse_qs(parsed.query)
            
            username = query_params.get('username', [None])[0]
            password = query_params.get('password', [None])[0]
            
            if not username or not password:
                return None
            
            server = parsed.hostname
            port = parsed.port or 80
            
            if not parsed.port:
                port = 443 if parsed.scheme == 'https' else 80
            
            return {
                'server': server,
                'port': port,
                'username': username,
                'password': password,
                'scheme': parsed.scheme or 'http'
            }
        except Exception as e:
            logger.error(f"Erro ao extrair credenciais: {str(e)}")
            return None
    
    def get_account_info(self, server: str, port: int, username: str, password: str, scheme: str = 'http') -> Optional[Dict]:
        """Consulta informações da conta na API Xtream Codes"""
        try:
            api_url = f"{scheme}://{server}:{port}/player_api.php?username={username}&password={password}"
            
            logger.info(f"Consultando API Xtream Codes: {api_url.replace(password, '***')}")
            
            response = self.session.get(api_url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'user_info' in data:
                user_info = data['user_info']
                
                created_at = user_info.get('created_at', '')
                exp_date = user_info.get('exp_date', '')
                
                created_date = self._timestamp_to_date(created_at) if created_at else 'N/A'
                exp_date_formatted = self._timestamp_to_date(exp_date) if exp_date else 'N/A'
                
                return {
                    'created_at': created_at,
                    'created_date': created_date,
                    'exp_date': exp_date,
                    'exp_date_formatted': exp_date_formatted,
                    'status': user_info.get('status', 'unknown'),
                    'is_trial': user_info.get('is_trial', False),
                    'active_cons': user_info.get('active_cons', 0),
                    'max_connections': user_info.get('max_connections', 0),
                    'full_info': user_info
                }
            else:
                logger.warning("Resposta da API não contém 'user_info'")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar API Xtream Codes: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar API: {str(e)}")
            return None
    
    def _timestamp_to_date(self, timestamp: str) -> str:
        """Converte timestamp Unix para data legível"""
        try:
            if not timestamp or timestamp == '0':
                return 'N/A'
            
            ts = int(timestamp)
            if ts == 0:
                return 'N/A'
            
            dt = datetime.fromtimestamp(ts)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError, OSError):
            return 'N/A'


class IPTVTester:
    """Classe para testar listas IPTV"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def test_m3u_url(self, m3u_url: str) -> Dict:
        """Testa um link M3U"""
        results = {
            'url': m3u_url,
            'accessible': False,
            'valid_m3u': False,
            'total_channels': 0,
            'errors': []
        }
        
        try:
            logger.info("Verificando acessibilidade do link M3U...")
            response = self.session.get(m3u_url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            results['accessible'] = True
            
            logger.info("Verificando formato M3U...")
            content = response.text
            if not content.strip().startswith('#EXTM3U'):
                results['errors'].append("Arquivo não é um M3U válido")
                return results
            
            results['valid_m3u'] = True
            
            logger.info("Contando canais...")
            channels = self._count_channels(content)
            results['total_channels'] = channels
            
            logger.info(f"Lista válida! Total de canais: {channels}")
            
        except requests.exceptions.RequestException as e:
            results['errors'].append(f"Erro ao acessar link: {str(e)}")
            logger.error(f"Erro ao testar lista: {str(e)}")
        except Exception as e:
            results['errors'].append(f"Erro inesperado: {str(e)}")
            logger.error(f"Erro inesperado: {str(e)}")
        
        return results
    
    def _count_channels(self, content: str) -> int:
        """Conta o número de canais no arquivo M3U"""
        count = 0
        lines = content.split('\n')
        
        for line in lines:
            if line.strip().startswith('#EXTINF:'):
                count += 1
        
        return count


def init_csv_file():
    """Inicializa o arquivo CSV com cabeçalhos se não existir"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
        logger.info(f"Arquivo CSV criado: {CSV_FILE}")


def save_to_csv(m3u_url: str, server: str, port: int, username: str, password: str,
                created_date: str, exp_date: str, total_channels: int, 
                status: str, canal_origem: str, mensagem_id: int, observacoes: str = ''):
    """Salva informações da lista IPTV no arquivo CSV"""
    try:
        init_csv_file()
        
        row = {
            'link_m3u': m3u_url,
            'servidor': server,
            'porta': str(port),
            'username': username,
            'password': password,
            'data_criacao': created_date,
            'data_vencimento': exp_date,
            'total_canais': str(total_channels),
            'status': status,
            'data_teste': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'canal_origem': canal_origem,
            'mensagem_id': str(mensagem_id),
            'observacoes': observacoes
        }
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow(row)
        
        logger.info(f"Lista salva no CSV: {m3u_url}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar no CSV: {str(e)}")


def detect_m3u_links(texto: str) -> List[str]:
    """Detecta links M3U no texto"""
    # Padrão para detectar URLs M3U Xtream Codes
    patterns = [
        r'https?://[^\s\)\]\"]+get\.php[^\s\)\]\"]*type=m3u[^\s\)\]\"]*',
        r'https?://[^\s\)\]\"]+\.m3u[^\s\)\]\"]*',
        r'https?://[^\s\)\]\"]+username=[^\s\)\]\"]*password=[^\s\)\]\"]*',
    ]
    
    links = []
    for pattern in patterns:
        found = re.findall(pattern, texto, re.IGNORECASE)
        links.extend(found)
    
    # Remover duplicatas e limpar
    links = list(set([link.strip() for link in links if link.strip()]))
    
    return links


def substituir_palavras_especificas(texto: str, substituicoes: dict) -> str:
    """Substitui palavras específicas no texto"""
    if not substituicoes or not texto:
        return texto
    
    texto_modificado = texto
    for palavra_original, palavra_nova in substituicoes.items():
        pattern = re.compile(re.escape(palavra_original), re.IGNORECASE)
        texto_modificado = pattern.sub(palavra_nova, texto_modificado)
        print(f"[INFO] Substituído: '{palavra_original}' -> '{palavra_nova}'")
    
    return texto_modificado


class Configuracao:
    """Classe de configuração do bot"""
    
    def __init__(self):
        # Credenciais do Telegram
        api_id_raw = os.getenv('API_ID')
        api_hash_raw = os.getenv('API_HASH')
        if not api_id_raw or not api_hash_raw:
            raise ValueError('API_ID e API_HASH devem estar definidos!')
        self.api_id = int(api_id_raw)
        self.api_hash = str(api_hash_raw)
        
        # Lista de canais de origem
        canais_origem_raw = os.getenv('CANAL_ORIGEM', '')
        self.canais_origem = [c.strip() for c in canais_origem_raw.split(',') if c.strip()]
        
        if not self.canais_origem:
            raise ValueError('Pelo menos um CANAL_ORIGEM deve estar definido!')
        
        # Testar automaticamente links M3U encontrados
        self.testar_automatico = os.getenv('TESTAR_AUTOMATICO', 'true').lower() == 'true'
        
        # Palavras-chave (opcional)
        self.palavras_chave = [p.strip().lower() for p in os.getenv('PALAVRAS_CHAVE', '').split(',') if p.strip()]
        
        # Palavras bloqueadas
        self.palavras_bloqueadas = [p.strip().lower() for p in os.getenv('PALAVRAS_BLOQUEADAS', '').split(',') if p.strip()]
        
        # Substituições
        substituicoes_raw = os.getenv('SUBSTITUICOES', '')
        self.substituicoes = {}
        if substituicoes_raw:
            for item in substituicoes_raw.split(','):
                if ':' in item:
                    original, nova = item.split(':', 1)
                    self.substituicoes[original.strip()] = nova.strip()
        
        # Timeout para requisições IPTV
        self.iptv_timeout = int(os.getenv('IPTV_TIMEOUT', '15'))
        
        # URL do webhook do n8n (opcional)
        self.webhook_url = os.getenv('WEBHOOK_URL', '')
        
        # Timeout para requisições webhook
        self.webhook_timeout = int(os.getenv('WEBHOOK_TIMEOUT', '30'))


# Inicializar configuração
try:
    config = Configuracao()
except ValueError as e:
    print(f"[ERRO] Erro de configuração: {e}")
    exit(1)

# Inicializar componentes
xtream_api = XtreamCodesAPI(timeout=config.iptv_timeout)
iptv_tester = IPTVTester(timeout=config.iptv_timeout)
webhook_sender = WebhookSender(config.webhook_url, timeout=config.webhook_timeout) if config.webhook_url else None
client = TelegramClient(os.path.join(DATA_DIR, 'session_iptv_bot'), config.api_id, config.api_hash)

# Inicializar CSV
init_csv_file()


@client.on(events.NewMessage(chats=config.canais_origem))
async def handler(event):
    """Handler para novas mensagens"""
    mensagem = event.message
    texto = mensagem.text or mensagem.message or ''
    
    canal_titulo = event.chat.title if hasattr(event.chat, 'title') else 'Desconhecido'
    canal_id = event.chat.id if hasattr(event.chat, 'id') else None
    
    print(f"\n[INFO] Nova mensagem recebida de {canal_titulo}")
    print(f"[INFO] Texto: {texto[:100]}..." if len(texto) > 100 else f"[INFO] Texto: {texto}")
    
    # Verificar palavras-chave (se configuradas)
    if config.palavras_chave:
        if not any(p in texto.lower() for p in config.palavras_chave):
            print(f"[IGNORADO] Mensagem não contém palavras-chave")
            return
    
    # Verificar palavras bloqueadas
    if config.palavras_bloqueadas:
        if any(p in texto.lower() for p in config.palavras_bloqueadas):
            print(f"[BLOQUEADO] Mensagem bloqueada por conter palavra proibida")
            return
    
    # Substituir palavras específicas
    texto_modificado = substituir_palavras_especificas(texto, config.substituicoes)
    
    # Detectar links M3U
    m3u_links = detect_m3u_links(texto)
    
    # Processar links M3U se encontrados e se teste automático estiver ativado
    if m3u_links and config.testar_automatico:
        print(f"[INFO] {len(m3u_links)} link(s) M3U detectado(s)")
        
        for m3u_url in m3u_links:
            print(f"\n[INFO] Processando link M3U: {m3u_url[:80]}...")
            
            # Testar lista IPTV
            test_results = iptv_tester.test_m3u_url(m3u_url)
            
            if not test_results['accessible'] or not test_results['valid_m3u']:
                print(f"[ERRO] Lista IPTV inválida ou inacessível")
                print(f"Erros: {test_results['errors']}")
                continue
            
            # Extrair credenciais Xtream Codes
            credentials = xtream_api.extract_credentials(m3u_url)
            
            if not credentials:
                print(f"[ERRO] Não foi possível extrair credenciais Xtream Codes")
                continue
            
            # Consultar API Xtream Codes
            account_info = xtream_api.get_account_info(
                server=credentials['server'],
                port=credentials['port'],
                username=credentials['username'],
                password=credentials['password'],
                scheme=credentials['scheme']
            )
            
            if not account_info:
                print(f"[ERRO] Não foi possível consultar API Xtream Codes")
                continue
            
            # Salvar no CSV
            observacoes = f"Status: {account_info.get('status', 'unknown')}, "
            observacoes += f"Trial: {account_info.get('is_trial', False)}, "
            observacoes += f"Conexões: {account_info.get('active_cons', 0)}/{account_info.get('max_connections', 0)}"
            
            save_to_csv(
                m3u_url=m3u_url,
                server=credentials['server'],
                port=credentials['port'],
                username=credentials['username'],
                password=credentials['password'],
                created_date=account_info['created_date'],
                exp_date=account_info['exp_date_formatted'],
                total_channels=test_results['total_channels'],
                status=account_info.get('status', 'unknown'),
                canal_origem=canal_titulo,
                mensagem_id=mensagem.id,
                observacoes=observacoes
            )
            
            print(f"[OK] Lista IPTV válida e salva no CSV!")
            print(f"  • Canais: {test_results['total_channels']}")
            print(f"  • Status: {account_info.get('status', 'unknown')}")
            print(f"  • Vencimento: {account_info['exp_date_formatted']}")
            
            # Enviar para webhook do n8n se configurado
            if webhook_sender:
                dados_webhook = {
                    'timestamp': datetime.now().isoformat(),
                    'tipo': 'lista_iptv_valida',
                    'link_m3u': m3u_url,
                    'servidor': credentials['server'],
                    'porta': credentials['port'],
                    'username': credentials['username'],
                    'password': credentials['password'],
                    'data_criacao': account_info['created_date'],
                    'data_vencimento': account_info['exp_date_formatted'],
                    'total_canais': test_results['total_channels'],
                    'status': account_info.get('status', 'unknown'),
                    'is_trial': account_info.get('is_trial', False),
                    'active_cons': account_info.get('active_cons', 0),
                    'max_connections': account_info.get('max_connections', 0),
                    'canal_origem': {
                        'titulo': canal_titulo,
                        'id': canal_id
                    },
                    'mensagem': {
                        'id': mensagem.id,
                        'data': mensagem.date.isoformat() if mensagem.date else None
                    },
                    'teste': {
                        'accessible': test_results['accessible'],
                        'valid_m3u': test_results['valid_m3u'],
                        'total_channels': test_results['total_channels']
                    }
                }
                
                print(f"[INFO] Enviando dados para webhook do n8n...")
                sucesso = webhook_sender.send_iptv_data(dados_webhook)
                
                if sucesso:
                    print(f"[OK] Dados enviados com sucesso para o webhook")
                else:
                    print(f"[AVISO] Falha ao enviar para webhook (lista salva no CSV)")


async def enviar_para_webhook(nome_arquivo, conteudo):
    """Envia a lista extraída para o webhook N8N"""
    if not config.webhook_url:
        logger.warning("⚠️ WEBHOOK_URL não configurada. Pulando envio.")
        return False
    
    try:
        payload = {
            "timestamp": datetime.now().isoformat(),
            "arquivo": nome_arquivo,
            "conteudo": conteudo,
            "canal_origem": config.canais_origem
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=config.webhook_timeout)
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Enviado para webhook: {nome_arquivo}")
                    return True
                else:
                    logger.error(f"❌ Erro webhook ({response.status}): {await response.text()}")
                    return False
    except asyncio.TimeoutError:
        logger.error(f"⏱️ Timeout ao enviar para webhook (>{config.webhook_timeout}s)")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao enviar webhook: {e}")
        return False

async def processar_mensagem(message):
    """Processa mensagens do canal"""
    try:
        if not message.text and not message.document:
            return
        
        # Processa mensagens de texto com listas IPTV
        if message.text:
            conteudo = message.text
            
            # Detecta formato (m3u, txt, etc)
            if conteudo.strip().startswith('#EXTM3U') or 'http' in conteudo:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"lista_{timestamp}.m3u"
                caminho = os.path.join(LISTS_DIR, nome_arquivo)
                
                # Salva localmente
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                
                logger.info(f"💾 Salvo: {nome_arquivo}")
                
                # Envia para webhook
                await enviar_para_webhook(nome_arquivo, conteudo)
        
        # Processa documentos (arquivos .m3u, .txt)
        if message.document:
            arquivo = await client.download_media(message.document, file=str(LISTS_DIR))
            if arquivo:
                nome_arquivo = os.path.basename(arquivo)
                logger.info(f"📥 Downloaded: {nome_arquivo}")
                
                # Lê conteúdo do arquivo
                with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                    conteudo = f.read()
                
                # Envia para webhook
                await enviar_para_webhook(nome_arquivo, conteudo)
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")

@client.on(events.NewMessage(chats=config.canais_origem))
async def handler(event):
    """Handler para novas mensagens"""
    await processar_mensagem(event.message)

async def main():
    """Função principal"""
    await client.start()
    logger.info(f"🚀 Bot iniciado. Monitorando canal: {config.canais_origem}")
    logger.info(f"🔗 Webhook: {config.webhook_url if config.webhook_url else 'NÃO CONFIGURADO'}")
    await client.run_until_disconnected()

if __name__ == '__main__':
    iniciar_bot()
