#python base image
From python:3.11-slim
# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get uppdate && apt-get install -y \
    wget \
    gnupg \
    unzip \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

#adiciona google chrome 
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

#installar chromedriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

#copia reqeuirements file
COPY requirements.txt .

#install Python (Gunicorn é um servidor WSGI de produção para Flask)
RUN pip install --no-cache-dir -r requirements.txt

#copia all files for directory
COPY . .

#expose port app
EXPOSE 5000

#comando para iniciar 
#usar o Gunicorn para servidor 
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]