# 🚀 Quick Start - Video Remix Agent

## ⚡ Rodar Localmente (Computador)

### **Pré-requisitos:**
```bash
# Python 3.10+
python3 --version

# FFmpeg
ffmpeg -version

# Node.js (para Hyperframes no futuro)
node --version
```

### **1️⃣ Clonar o Projeto**
```bash
git clone https://github.com/seu-username/mcp-video-remix-agente.git
cd mcp-video-remix-agente
git checkout claude/video-editing-automation-SoRC4
```

### **2️⃣ Instalar Dependências**
```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instalar pacotes
pip install -r requirements.txt
```

### **3️⃣ Configurar API**
```bash
cp .env.example .env
# Edite .env e adicione:
# ELEVENLABS_API_KEY=sk-seu-token-aqui
```

### **4️⃣ Rodar o Servidor**
```bash
python3 app.py
```

Você verá:
```
🚀 Servidor Flask rodando em http://0.0.0.0:8000
📍 Acesse: http://localhost:8000
```

---

## 📱 Acessar pelo Celular

Se você está na **mesma WiFi** que o computador:

1. Abra terminal e rode: `ifconfig` (macOS) ou `ipconfig` (Windows)
2. Procure o IP da máquina (ex: `192.168.1.100`)
3. No celular, acesse: `http://192.168.1.100:8000`

---

## 🎬 Usar o Sistema

1. **Upload**: Selecione um vídeo
2. **Processar**: Escolha estilo de animação
3. **Resultado**: Baixe o vídeo editado

---

## 🐳 Deploy em Nuvem (Docker)

```bash
# Build da imagem
docker build -t video-remix .

# Rodar localmente
docker run -p 8000:8000 video-remix
```

---

## 📋 Requisitos do Sistema

| Componente | Versão |
|---|---|
| Python | ≥ 3.10 |
| FFmpeg | ≥ 4.0 |
| Node.js | ≥ 22 |
| RAM | 4GB+ |
| Disco | 10GB+ (para processamento) |

---

## 🆘 Troubleshooting

### "Port 8000 já está em uso"
```bash
python3 app.py --port 9000
```

### "FFmpeg not found"
```bash
# macOS
brew install ffmpeg

# Ubuntu/Linux
sudo apt-get install ffmpeg

# Windows: Baixe em https://ffmpeg.org/download.html
```

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask werkzeug
```

---

## 📚 Mais Informações

- **README.md**: Explicação completa do projeto
- **ARCHITECTURE.md**: Detalhes técnicos da arquitetura
- **index.html**: Página web com interface

---

**Pronto para editar seus vídeos!** 🎉
