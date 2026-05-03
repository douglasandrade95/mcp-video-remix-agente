import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import HYPERFRAMES_PATH

class HyperframesHandler:
    """Handler para integração com Hyperframes (animações sincronizadas)"""

    def __init__(self):
        self.hyperframes_path = Path(HYPERFRAMES_PATH)

    async def generate_animations(
        self,
        video_processado: str,
        transcricao: Dict,
        edit_dir: str,
        animation_style: str = "minimal"
    ) -> Dict[str, Any]:
        """
        Gera HTML com animações GSAP sincronizadas com a transcrição

        Args:
            video_processado: path do vídeo processado
            transcricao: dict com dados de transcrição (words, text)
            edit_dir: diretório de edição
            animation_style: estilo de animações ("minimal", "vibrant", "cinematic")

        Returns:
            {
                "status": "sucesso/erro",
                "html_path": str,
                "composicao": dict,  # metadados da composição
                "frames": int,
                "duracao": float
            }
        """
        try:
            edit_path = Path(edit_dir)
            composicoes_dir = edit_path / "compositions"
            composicoes_dir.mkdir(parents=True, exist_ok=True)

            # Gerar HTML com animações
            html_content = await self._gerar_html(
                transcricao,
                animation_style,
                edit_dir
            )

            if not html_content:
                return {
                    "status": "erro",
                    "mensagem": "Falha ao gerar HTML"
                }

            # Salvar HTML
            html_path = composicoes_dir / "index.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Obter metadados da composição (duração, etc)
            composicao = await self._analisar_composicao(str(html_path), transcricao)

            return {
                "status": "sucesso",
                "html_path": str(html_path),
                "composicao": composicao,
                "frames": int(composicao.get("duracao", 0) * 24),  # 24 FPS
                "duracao": composicao.get("duracao", 0)
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": str(e)
            }

    async def render_with_animations(
        self,
        html_path: str,
        video_processado: str,
        edit_dir: str,
        fps: int = 24
    ) -> Dict[str, Any]:
        """
        Renderiza vídeo com animações usando Hyperframes CLI

        Fluxo:
        1. Preparar projeto Hyperframes
        2. Copiar HTML para projeto
        3. Executar npx hyperframes render
        4. Muxar áudio original

        Returns:
            {
                "status": "sucesso/erro",
                "video_final": str,  # path do vídeo final
                "duracao": float,
                "fps": int
            }
        """
        try:
            # Criar projeto Hyperframes temporário
            project_dir = Path(edit_dir) / "hyperframes_project"
            await self._criar_projeto(str(project_dir))

            # Copiar HTML para projeto
            html_dest = project_dir / "src" / "index.html"
            html_dest.parent.mkdir(parents=True, exist_ok=True)

            with open(html_path) as src:
                html_content = src.read()
            with open(html_dest, 'w') as dst:
                dst.write(html_content)

            # Renderizar com Hyperframes
            render_output = project_dir / "output.mp4"
            success = await self._executar_render(
                str(project_dir),
                str(render_output),
                fps
            )

            if not success or not render_output.exists():
                return {
                    "status": "erro",
                    "mensagem": "Falha ao renderizar com Hyperframes"
                }

            # Extrair áudio do vídeo processado e muxar
            video_final = Path(edit_dir) / "video_final.mp4"
            sucesso_mux = await self._muxar_audio(
                str(render_output),
                video_processado,
                str(video_final)
            )

            if not sucesso_mux:
                return {
                    "status": "erro",
                    "mensagem": "Falha ao muxar áudio"
                }

            # Obter duração
            duracao = await self._obter_duracao(str(video_final))

            return {
                "status": "sucesso",
                "video_final": str(video_final),
                "duracao": duracao,
                "fps": fps
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": str(e)
            }

    # ===== MÉTODOS PRIVADOS =====

    async def _gerar_html(
        self,
        transcricao: Dict,
        animation_style: str,
        edit_dir: str
    ) -> Optional[str]:
        """Gera HTML com GSAP timelines para animações sincronizadas"""
        try:
            palavras = transcricao.get("words", [])
            texto_completo = transcricao.get("text", "")
            duracao_total = 0

            if palavras:
                duracao_total = max(w.get("end", 0) for w in palavras)

            # Configurações de animação por estilo
            estilos = {
                "minimal": {
                    "bg": "#ffffff",
                    "text_color": "#000000",
                    "accent": "#4f46e5",
                    "efeitos": ["fade", "scale"]
                },
                "vibrant": {
                    "bg": "#1a1a2e",
                    "text_color": "#ffffff",
                    "accent": "#ff006e",
                    "efeitos": ["slide", "rotate", "scale"]
                },
                "cinematic": {
                    "bg": "#0a0e27",
                    "text_color": "#e0e0e0",
                    "accent": "#00d9ff",
                    "efeitos": ["blur", "fade", "slideUp"]
                }
            }

            config = estilos.get(animation_style, estilos["minimal"])

            # Gerar HTML
            html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Composition</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: {config['bg']};
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            color: {config['text_color']};
            overflow: hidden;
        }}

        #stage {{
            width: 1920px;
            height: 1080px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }}

        .title {{
            font-size: 64px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 40px;
            letter-spacing: -1px;
            line-height: 1.2;
        }}

        .subtitle {{
            font-size: 32px;
            text-align: center;
            opacity: 0.8;
            font-weight: 300;
        }}

        .keywords {{
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 60px;
            flex-wrap: wrap;
        }}

        .keyword {{
            padding: 12px 24px;
            background: {config['accent']};
            color: white;
            border-radius: 50px;
            font-weight: 600;
            font-size: 18px;
        }}

        .accent-line {{
            width: 100px;
            height: 4px;
            background: {config['accent']};
            margin: 30px auto;
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div id="stage" data-composition-id="video-remix" data-start="0" data-width="1920" data-height="1080">
        <div class="title" id="mainTitle">
            {texto_completo[:100] if texto_completo else 'Video Composition'}
        </div>
        <div class="accent-line"></div>
        <div class="subtitle" id="subtitle">
            Editado automaticamente com Video Use + Hyperframes
        </div>
        <div class="keywords" id="keywords">
'''

            # Adicionar palavras-chave como badges
            palavras_chave = transcricao.get("palavras_chave", [])[:5]
            for palavra in palavras_chave:
                html += f'            <div class="keyword">{palavra}</div>\n'

            html += '''        </div>
    </div>

    <script>
        // Timeline principal de animações
        const timeline = gsap.timeline({ paused: true });

        // Animação de entrada do título
        timeline.from("#mainTitle", {
            opacity: 0,
            y: 50,
            duration: 1
        }, 0);

        // Animação da linha de acentuação
        timeline.from(".accent-line", {
            width: 0,
            duration: 0.8
        }, 0.2);

        // Animação do subtítulo
        timeline.from("#subtitle", {
            opacity: 0,
            y: 30,
            duration: 0.8
        }, 0.5);

        // Animação das keywords
        timeline.from(".keyword", {
            opacity: 0,
            scale: 0.8,
            duration: 0.5,
            stagger: 0.1
        }, 0.8);

        // Exportar timeline para uso do Hyperframes
        window.__hfTimeline = timeline;
        window.__hfDuration = ''' + str(duracao_total) + ''';

        // Sinalizar que está pronto para o Hyperframes
        if (window.__renderReady) {
            window.__renderReady();
        }
    </script>
</body>
</html>'''

            return html

        except Exception as e:
            print(f"Exceção em _gerar_html: {e}", file=sys.stderr)
            return None

    async def _analisar_composicao(self, html_path: str, transcricao: Dict) -> Dict:
        """Analisar composição para obter metadados"""
        try:
            palavras = transcricao.get("words", [])
            duracao = 0

            if palavras:
                duracao = max(w.get("end", 0) for w in palavras)

            return {
                "duracao": duracao + 2,  # +2 segundos para animações de saída
                "fps": 24,
                "largura": 1920,
                "altura": 1080,
                "animacoes": ["fade", "scale", "slide"]
            }

        except Exception:
            return {"duracao": 10, "fps": 24, "largura": 1920, "altura": 1080}

    async def _criar_projeto(self, project_dir: str) -> bool:
        """Criar estrutura básica de projeto Hyperframes"""
        try:
            project_path = Path(project_dir)
            project_path.mkdir(parents=True, exist_ok=True)

            # Criar package.json mínimo
            package_json = {
                "name": "video-remix-composition",
                "version": "1.0.0",
                "type": "module",
                "dependencies": {
                    "hyperframes": "latest"
                }
            }

            with open(project_path / "package.json", 'w') as f:
                json.dump(package_json, f, indent=2)

            # Criar diretório src
            src_dir = project_path / "src"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Criar index.html placeholder
            with open(src_dir / "index.html", 'w') as f:
                f.write("<html><body>Loading...</body></html>")

            return True

        except Exception as e:
            print(f"Exceção em _criar_projeto: {e}", file=sys.stderr)
            return False

    async def _executar_render(
        self,
        project_dir: str,
        output_path: str,
        fps: int = 24
    ) -> bool:
        """Executar hyperframes render via CLI"""
        try:
            # Instalar dependências
            install_cmd = ["npm", "install"]
            result = subprocess.run(
                install_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                print(f"Erro ao instalar deps: {result.stderr}", file=sys.stderr)

            # Renderizar
            render_cmd = [
                "npx",
                "hyperframes",
                "render",
                "-o",
                output_path,
                "--fps",
                str(fps)
            ]

            result = subprocess.run(
                render_cmd,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=600
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Exceção em _executar_render: {e}", file=sys.stderr)
            return False

    async def _muxar_audio(
        self,
        video_sem_audio: str,
        video_original: str,
        output_path: str
    ) -> bool:
        """Muxar áudio do vídeo original com o vídeo renderizado"""
        try:
            # Extrair áudio
            audio_path = str(Path(output_path).parent / "audio_temp.aac")

            extract_cmd = [
                "ffmpeg",
                "-i", video_original,
                "-q:a", "9",
                "-map", "a",
                audio_path,
                "-y"
            ]

            result = subprocess.run(
                extract_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                print(f"Erro ao extrair áudio: {result.stderr}", file=sys.stderr)
                return False

            # Muxar
            mux_cmd = [
                "ffmpeg",
                "-i", video_sem_audio,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                output_path,
                "-y"
            ]

            result = subprocess.run(
                mux_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Limpar áudio temporário
            Path(audio_path).unlink(missing_ok=True)

            return result.returncode == 0

        except Exception as e:
            print(f"Exceção em _muxar_audio: {e}", file=sys.stderr)
            return False

    async def _obter_duracao(self, video_path: str) -> float:
        """Obter duração do vídeo usando ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1:noescapes=1",
                video_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return float(result.stdout.strip())

            return 0.0

        except Exception:
            return 0.0
