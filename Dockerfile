# Use imagem Python 3.11 slim
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Define variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY telegram_iptv_bot.py .

# Cria volume para dados persistentes
VOLUME ["/app/data"]

# Comando para iniciar o bot
CMD ["python", "telegram_iptv_bot.py"]
