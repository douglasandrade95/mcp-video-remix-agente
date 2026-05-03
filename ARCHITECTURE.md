# Arquitetura: Video Remix Agent

## 📐 Visão Geral

```
┌─────────────────────────────────────────────────────┐
│         Claude Code / Chat (User Interface)         │
└─────────────────────┬───────────────────────────────┘
                      │
                      │ File upload (video)
                      ▼
        ┌─────────────────────────────┐
        │   mcp-video-remix-agente    │
        │   (MCP Server - Python 3.10)│
        │  (mcp_server.py)            │
        └──────┬──────────────────┬───┘
               │                  │
        ┌──────▼──────┐    ┌──────▼──────────┐
        │ Video Use   │    │  Hyperframes    │
        │ Handler     │    │  Handler        │
        │ (Python)    │    │  (Python Wrap)  │
        └──────┬──────┘    └──────┬──────────┘
               │                  │
        ┌──────▼──────────┐  ┌────▼──────────────┐
        │ external/       │  │ external/         │
        │ video-use/      │  │ hyperframes/      │
        │ helpers/        │  │ packages/cli/     │
        │ - transcribe.py │  │ (Node.js binary)  │
        │ - render.py     │  │                   │
        │ - grade.py      │  │                   │
        └──────┬──────────┘  └────┬──────────────┘
               │                  │
        ┌──────▼──────────┐  ┌────▼──────────────┐
        │ ElevenLabs      │  │ Puppeteer         │
        │ Scribe API      │  │ (Browser engine)  │
        │                 │  │ → FFmpeg (mux)    │
        │                 │  │ → VP9/H.264       │
        └─────────────────┘  └───────────────────┘
                      │
                      │
                      ▼
        ┌─────────────────────────────┐
        │  workspace/                 │
        │  ├── video_processado.mp4   │
        │  ├── video_final.mp4        │
        │  ├── transcricao.json       │
        │  ├── edl.json               │
        │  └── compositions/          │
        │      └── index.html (GSAP)  │
        └─────────────────────────────┘
```

## 🔄 Pipeline Detalhado

### Etapa 1: Remoção de Silêncios (Video Use)

**Handler**: `VideoUseHandler` (handlers/video_use_handler.py)

**Processo**:

```python
process_video(video_path: str, edit_dir: str)
    │
    ├─► 1. Transcrição (ElevenLabs Scribe)
    │       - ffprobe → extrai áudio
    │       - API call → word-level timestamps
    │       - Cacheado em transcripts/
    │
    ├─► 2. Grouping de Transcription
    │       - Agrupa palavras em takes
    │       - Detecta silêncios > 0.5s
    │       - Cria takes_packed.md
    │
    ├─► 3. Geração de EDL
    │       - Analisa transcrição
    │       - Cria ranges removendo silêncios
    │       - Preserva word boundaries
    │       - Calcula duração final
    │
    └─► 4. Renderização
            - ffmpeg concat segments
            - aplica color grading
            - fade 30ms em cortes
            - output: video_processado.mp4
```

**Input**: `.mp4` raw com silêncios
**Output**: 
- `video_processado.mp4` (silêncios removidos)
- `transcricao.json` (word-level data)
- `edl.json` (Edit Decision List)
- `timeline.png` (visualização)

**Redução típica**: 20-30% de duração

---

### Etapa 2: Animações Sincronizadas (Hyperframes)

**Handler**: `HyperframesHandler` (handlers/hyperframes_handler.py)

**Processo**:

```python
generate_animations(video, transcription, style)
    │
    └─► 1. Análise de Transcrição
            - Extrai palavras-chave (top 5)
            - Detecta mudanças de tom/ritmo
            - Mapeia timings
            │
    └─► 2. Geração de HTML/CSS
            - Template base (GSAP)
            - Estilo: minimal/vibrant/cinematic
            - Timelines sincronizadas
            - output: compositions/index.html
            │
    └─► 3. Renderização (Hyperframes CLI)
            - npm install em projeto temp
            - npx hyperframes render
            - Puppeteer captura frames
            - VP9/H.264 encoding via ffmpeg
            │
    └─► 4. Muxing de Áudio
            - Extrai áudio original
            - Combina com vídeo renderizado
            - output: video_final.mp4
```

**Input**: 
- `video_processado.mp4`
- `transcricao.json`
- `estilo: "minimal" | "vibrant" | "cinematic"`

**Output**: 
- `video_final.mp4` (com animações)
- Duração = duração do áudio original
- FPS: 24 (configurável)

**Estilos**:
- **minimal**: Fundo branco, text dark, animações fade/scale
- **vibrant**: Fundo dark, text light, animações slide/rotate
- **cinematic**: Fundo muito escuro, accent cyan, blur effects

---

### Etapa 3: Orquestração (mcp_server.py)

**Função Principal**: `_editar_video_completo()`

```
editar_video(video_path, estilo_animacao, remover_silencio)
    │
    ├─ remover_silencio=true?
    │  │
    │  ├─► VideoUseHandler.process_video()
    │  │   └─► video_processado + transcricao
    │  │
    │  └─► Caso contrário: analyze_video()
    │      └─► transcrição do original
    │
    ├─► HyperframesHandler.generate_animations()
    │   └─► HTML com GSAP timelines
    │
    ├─► HyperframesHandler.render_with_animations()
    │   └─► video_final.mp4
    │
    └─► Retorna resultado com:
        - video_final path
        - duracao_final
        - fps
        - etapas executadas
```

---

## 📁 Estrutura de Arquivos

### workspace/
Criado automaticamente com um diretório por vídeo processado:

```
workspace/
└── meu_video/                      # {stem do input}
    ├── transcripts/
    │   └── meu_video.json         # Resultado Scribe
    │
    ├── takes_packed.md            # Agrupamento de palabras
    ├── edl.json                   # Edit Decision List
    │
    ├── compositions/
    │   └── index.html             # HTML/GSAP
    │
    ├── hyperframes_project/       # Projeto Hyperframes temp
    │   ├── package.json
    │   ├── src/index.html
    │   └── output.mp4             # Renderização intermediária
    │
    ├── video_processado.mp4       # Silêncios removidos
    ├── video_final.mp4            # Com animações + áudio
    │
    └── timeline.png               # Visual do waveform
```

---

## 🔧 Dependências Técnicas

### Python
```
anthropic>=0.7.0        # Para análise com Claude (futuro)
requests>=2.31.0        # HTTP calls para APIs
python-dotenv>=1.0.0    # .env vars
pydantic>=2.0.0         # Validação de dados
stdio-mcp>=0.1.0        # MCP protocol
librosa>=0.10.0         # Análise de áudio
numpy>=1.24.0           # Operações numéricas
```

### Binários do Sistema
```
ffmpeg                  # Encoding, extracting audio, muxing
ffprobe                 # Análise de vídeo
node >=22               # Para Hyperframes CLI
npm/bun                 # Package management
```

### APIs Externas
```
ElevenLabs Scribe       # Transcrição (word-level, diarização)
Freepik (opcional)      # Geração de imagens/vídeos
Claude (opcional)       # Análise cinematográfica
```

---

## 🚦 Fluxo de Dados

```
Raw Video
    ↓
[FFprobe] → Metadados (duração, codec, sample rate)
    ↓
[ElevenLabs] → Words [ {start: 0.5, end: 1.2, text: "hello"}, ... ]
    ↓
[Grouping] → Takes [ {words: [...], gap_after: 0.8s}, ... ]
    ↓
[EDL Gen] → Ranges [ {start: 0.5, end: 1.2, source: "C0"}, ... ]
    ↓
[FFmpeg] → Video Processado (silêncios removidos)
    ↓
[HTML Gen] → HTML com GSAP ( timeline.seek(frame_time) )
    ↓
[Puppeteer] → Frame extraction (determinístico)
    ↓
[FFmpeg] → H.264 encoding
    ↓
[Audio Extract] → .aac from original
    ↓
[Mux] → Final MP4 (vídeo + áudio original)
```

---

## ⚙️ Configuração (config.py)

```python
# Paths
BASE_DIR = Path(__file__).parent
EXTERNAL_DIR = BASE_DIR / "external"
VIDEO_USE_PATH = EXTERNAL_DIR / "video-use"
HYPERFRAMES_PATH = EXTERNAL_DIR / "hyperframes"
WORKSPACE_DIR = BASE_DIR / "workspace"

# Video specs
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 24

# APIs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY", "")
```

---

## 🧪 Teste Local

### Setup Completo
```bash
# 1. Instalar deps
pip install -r requirements.txt
brew install ffmpeg node

# 2. Config
cp .env.example .env
export ELEVENLABS_API_KEY=sk-xxxx

# 3. Run server (standalone test)
python mcp_server.py

# 4. Testar handlers
python -c "
import asyncio
from handlers.video_use_handler import VideoUseHandler

async def test():
    vu = VideoUseHandler()
    result = await vu.analyze_video('test.mp4', '/tmp/test')
    print(result)

asyncio.run(test())
"
```

---

## 🔮 Melhorias Futuras

1. **Batch Processing**: Múltiplos vídeos em paralelo
2. **Customização de Animações**: Templates customizados
3. **Cache Inteligente**: Reutilizar transcrições
4. **Streaming**: Live preview de renderização
5. **ML Análise**: Detectar emoticon/sentiment para animações automáticas
6. **Multi-Language**: Suporte a transcrição multilíngue
7. **Subtítulos**: Auto-generate SRT/VTT sincronizados
8. **Status Tracking**: WebSocket updates de progresso
