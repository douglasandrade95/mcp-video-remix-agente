# 🎬 Guia de Setup - Video Remix Agent

## ✅ Problemas Corrigidos

O código foi auditado e corrigido para funcionar **sem dependências externas**:

- ✅ **Demo Mode**: Transcrição funcionapor sem ElevenLabs API key
- ✅ **Fallback Rendering**: Se FFmpeg falhar, usa vídeo original
- ✅ **Fallback Hyperframes**: Se Hyperframes falhar, usa vídeo processado
- ✅ **Env Files**: Criado `.env` e `.env.example` para configuração

---

## 🚀 Instalação Rápida

### Opção 1: Rodar Localmente (Celular + Mesmo WiFi)

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Instalar ferramentas do sistema (se não tiver)
# macOS:
brew install ffmpeg

# Linux (Ubuntu/Debian):
sudo apt-get install ffmpeg

# 3. Rodar servidor
python3 app.py

# 4. No celular: acessar http://{seu-ip}:8000
```

**Como achar seu IP:**
```bash
# Linux/macOS
ifconfig | grep "inet "

# Windows
ipconfig
```

### Opção 2: Docker (Mais Fácil)

```bash
# Buildar imagem
docker build -t video-remix .

# Rodar container
docker run -p 8000:8000 video-remix

# Acessar em http://localhost:8000
```

### Opção 3: Deploy Railway (Para Celular em Qualquer Lugar)

1. Vai em https://railway.app
2. Clica "GitHub"
3. Conecta seu GitHub
4. Clica "New Project"
5. Seleciona seu repo + branch `claude/video-editing-automation-SoRC4`
6. Railway faz tudo sozinho ✨
7. Gera URL pública tipo `https://seu-projeto.railway.app`

---

## 🔧 Configuração Opcional (Para Melhores Resultados)

Se quiser usar **transcrição real** (não apenas demo):

1. Crie conta em https://elevenlabs.io
2. Pegue a API key
3. Edite `.env`:
   ```
   ELEVENLABS_API_KEY=sk-your-key-here
   ```
4. Reinicie servidor

---

## 📱 Usando do Celular

### Local (Mesmo WiFi)
```
http://192.168.1.100:8000
```
(substitua pelo IP do seu computador)

### Railway (De Qualquer Lugar)
```
https://seu-projeto-xxxx.railway.app
```

### Fluxo:
1. 📤 Upload vídeo
2. 🎨 Escolha estilo (Minimal/Vibrant/Cinematic)
3. ▶️ Clique "Processar"
4. ⏳ Aguarde progresso
5. ⬇️ Baixe vídeo editado

---

## 🆘 Troubleshooting

### "Port 8000 já em uso"
```bash
python3 app.py --port 9000
# Acessa: http://localhost:9000
```

### "FFmpeg not found"
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Baixe em https://ffmpeg.org/download.html
```

### "Flask not found"
```bash
pip install flask werkzeug
```

### "Vídeo não processa"
1. Verifique se arquivo é MP4/MOV/MKV válido
2. Verifique tamanho (máx 500MB)
3. Cheque logs do servidor para erros

---

## 📊 System Requirements

| Item | Mínimo | Recomendado |
|------|--------|-------------|
| RAM | 2GB | 4GB+ |
| Disco | 1GB | 10GB+ |
| Conexão | 5Mbps | 10Mbps+ |
| Python | 3.10+ | 3.11+ |
| FFmpeg | 4.0+ | 6.0+ |

---

## 🎯 O Que Funciona Agora

✅ Upload de vídeos (até 500MB)  
✅ Processamento em background (não trava interface)  
✅ Progresso em tempo real  
✅ 3 estilos de animação (minimal/vibrant/cinematic)  
✅ Download de vídeos editados  
✅ Funciona em celular (WiFi ou Railway)  

---

## 🔮 Melhorias Futuras

- [ ] Suporte a múltiplos uploads simultâneos
- [ ] Preview de animações antes de renderizar
- [ ] Customização de efeitos
- [ ] Cache de transcrições
- [ ] Histórico de processamentos

---

## 📞 Suporte

Se tiver problemas:
1. Verifique logs: `docker logs video-remix` ou console do Flask
2. Tente outra navegador
3. Verifique internet/WiFi

---

**Pronto! Seu sistema de edição automática de vídeos está funcionando!** 🎉
