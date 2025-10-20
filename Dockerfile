# Usa uma imagem base leve do Python
FROM python:3.11-slim

# Impede prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza e instala dependências do sistema + Chromium + Chromedriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    unzip \
    curl \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgbm1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Define variáveis para Selenium reconhecer o Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Define diretório de trabalho
WORKDIR /app

# Copia dependências do Python e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do projeto
COPY . .

# Cria pasta de downloads, se usada pelo scraper
RUN mkdir -p vecteezy_downloads && chmod 777 vecteezy_downloads

EXPOSE 5000

# Environment variable for Flask
ENV FLASK_APP=app.py

# Run with gunicorn (production server)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "--timeout", "300", "app:app"]