FROM python:3.10-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js >= 22
RUN npm install -g n && n 22.0.0

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Hyperframes
RUN cd external/hyperframes && npm install || true && cd /app

# Criar diretório de workspace
RUN mkdir -p workspace

# Expor porta
EXPOSE 8000

# Comando para rodar o servidor
CMD ["python3", "app.py"]
