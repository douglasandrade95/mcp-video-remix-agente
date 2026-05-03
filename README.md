# MCP Video Remix Agente

Um MCP Server que automatiza edição de vídeos integrando **Video Use** (remoção de silêncios) e **Hyperframes** (animações sincronizadas).

## 🎯 Como Funciona

```
Upload de Vídeo
      ↓
[Video Use] → Remove silêncios & repetições
      ↓
[Transcrição] → Análise de áudio e texto
      ↓
[Hyperframes] → Gera HTML com animações GSAP
      ↓
[Render] → MP4 final com animações sincronizadas
```

## ✨ Features

- 🎬 **Remoção Automática de Silêncios** - Remove pausas e repetições usando transcrição
- 🎨 **Animações Sincronizadas** - Adiciona efeitos visuais sincronizados com o áudio
- 📝 **Transcrição Inteligente** - ElevenLabs Scribe com análise de palavra-chave
- 🎯 **Múltiplos Estilos** - minimal, vibrant, cinematic
- 🤖 **Pipeline Automático** - Orquestra Video Use + Hyperframes em uma única chamada
- 📊 **Metadados** - Retorna EDL, transcrição e duração reduzida

## 📋 Pré-requisitos

- **Python** >= 3.10
- **FFmpeg** + FFprobe
- **Node.js** >= 22 (para Hyperframes)
- **Chrome/Chromium** (instalado via Puppeteer)

### APIs Necessárias

```env
ELEVENLABS_API_KEY=sk-xxxx  # Para transcrição de áudio
FREEPIK_API_KEY=xxxx         # Opcional (para Freepik)
```

## 🚀 Setup Rápido

### 1. Clone o repo
```bash
git clone https://github.com/douglasandrade95/mcp-video-remix-agente
cd mcp-video-remix-agente
```

### 2. Instale dependências Python
```bash
pip install -r requirements.txt
```

### 3. Instale FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Baixe em https://ffmpeg.org/download.html
```

### 4. Configure variáveis de ambiente
```bash
cp .env.example .env
# Adicione suas chaves de API em .env:
# ELEVENLABS_API_KEY=sk-xxxx
# FREEPIK_API_KEY=xxxx (opcional)
```

### 5. Prepare os repositórios externos
Os repositórios Video Use e Hyperframes são clonados automaticamente para `external/`.

## 📝 Uso

### Via Claude Code

```python
# Ferramenta: editar_video
# Entrada: caminho do vídeo + estilo de animação
{
    "video_path": "/caminho/para/video.mp4",
    "estilo_animacao": "vibrant",  # minimal | vibrant | cinematic
    "remover_silencio": true
}

# Output: Vídeo final com animações sincronizadas
```

### Ferramentas Disponíveis

#### 1. **editar_video** (Pipeline Completo)
Remove silêncios e adiciona animações em uma única chamada.

```python
{
    "video_path": "meu_video.mp4",
    "estilo_animacao": "cinematic",
    "remover_silencio": true
}
# Retorna: video_final.mp4, duração_final, workspace
```

#### 2. **processar_video_use**
Apenas remove silêncios (sem animações).

```python
{
    "video_path": "meu_video.mp4"
}
# Retorna: video_processado.mp4, transcrição, EDL, redução de duração
```

#### 3. **analisar_video**
Extrai transcrição e timeline visual.

```python
{
    "video_path": "meu_video.mp4"
}
# Retorna: transcrição, timeline.png, palavras-chave
```

#### 4. **gerar_animacoes**
Gera HTML com animações para vídeo já processado.

```python
{
    "video_path": "video_processado.mp4",
    "transcricao_path": "transcricao.json",
    "estilo": "minimal"
}
# Retorna: HTML com GSAP animations, metadados
```

## 📂 Estrutura do Projeto

```
mcp-video-remix-agente/
├── mcp_server.py              # MCP Server principal
├── config.py                  # Configurações
├── requirements.txt           # Dependências Python
├── handlers/
│   ├── video_use_handler.py   # Integração com Video Use
│   ├── hyperframes_handler.py # Integração com Hyperframes
│   └── freepik_handler.py     # Integração com Freepik
├── external/                  # Repositórios clonados
│   ├── video-use/            # Video Use (helpers, transcribe.py, etc)
│   └── hyperframes/          # Hyperframes (packages, CLI)
└── workspace/                 # Arquivos temporários de processamento
```

## 🔄 Fluxo Técnico Detalhado

### Phase 1: Video Use Processing
1. **Transcrição**: ElevenLabs Scribe extrai word-level timestamps
2. **Grouping**: Palavras são agrupadas em takes com silêncio > 0.5s
3. **EDL Generation**: Cria Edit Decision List removendo silêncios
4. **Rendering**: FFmpeg renderiza vídeo processado

### Phase 2: Hyperframes Animation
1. **HTML Generation**: Cria composição com GSAP timelines
2. **Animation Styles**: Aplica efeitos baseado em estilo escolhido
3. **Browser Rendering**: Puppeteer captura frames determinísticos
4. **Audio Muxing**: Combina áudio original com vídeo renderizado

## 📊 Exemplo de Output

```json
{
  "status": "sucesso",
  "video_final": "/workspace/meu_video/video_final.mp4",
  "duracao_original": 120.5,
  "duracao_processada": 87.3,
  "reducao": "27.5%",
  "fps": 24,
  "etapas": [
    "✓ Silêncios removidos (27.5%)",
    "✓ Animações geradas",
    "✓ Vídeo final renderizado"
  ]
}
```

## 🛠️ Troubleshooting

### "ELEVENLABS_API_KEY not set"
```bash
# Adicione a chave em .env ou export
export ELEVENLABS_API_KEY=sk-xxxx
```

### "ffmpeg not found"
```bash
# Instale FFmpeg
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Linux
```

### "Chrome/Chromium not available"
Hyperframes instalará automaticamente via Puppeteer na primeira execução.

## 📚 Referências

- [Video Use](https://github.com/browser-use/video-use) - Video editing com Claude
- [Hyperframes](https://github.com/heygen-com/hyperframes) - Video rendering com HTML/GSAP
- [ElevenLabs](https://elevenlabs.io/) - Transcrição de áudio

## 📄 Licença

MIT
