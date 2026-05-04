import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from config import VIDEO_USE_PATH, ELEVENLABS_API_KEY

class VideoUseHandler:
    """Handler para integração com Video Use (remoção de silêncios/repetições)"""

    def __init__(self):
        self.video_use_path = Path(VIDEO_USE_PATH)
        self.helpers_path = self.video_use_path / "helpers"

    async def process_video(self, video_path: str, edit_dir: str) -> Dict[str, Any]:
        """
        Processa vídeo para remover silêncios e repetições

        Fluxo:
        1. Transcrever áudio (ElevenLabs Scribe)
        2. Agrupar transcrição em takes
        3. Gerar EDL (decisões de corte)
        4. Renderizar vídeo com ffmpeg

        Returns:
            {
                "status": "sucesso/erro",
                "video_processado": str,  # path do vídeo processado
                "transcricao": dict,      # dados da transcrição
                "edl": dict,              # edit decision list
                "duracao_original": float,
                "duracao_processada": float
            }
        """
        try:
            # Criar diretório de edição
            edit_path = Path(edit_dir)
            edit_path.mkdir(parents=True, exist_ok=True)

            # Etapa 1: Transcrever vídeo
            transcrição_json = await self._transcrever(video_path, edit_dir)
            if not transcrição_json:
                return {
                    "status": "erro",
                    "mensagem": "Falha na transcrição"
                }

            # Etapa 2: Agrupar transcrição
            packed_transcripts = await self._agrupar_transcricao(edit_dir)
            if not packed_transcripts:
                return {
                    "status": "erro",
                    "mensagem": "Falha ao agrupar transcrição"
                }

            # Etapa 3: Gerar EDL (análise de silêncios)
            edl_json = await self._gerar_edl(video_path, transcrição_json, edit_dir)
            if not edl_json:
                return {
                    "status": "erro",
                    "mensagem": "Falha ao gerar EDL"
                }

            # Etapa 4: Renderizar vídeo
            video_processado = await self._renderizar(edl_json, edit_dir)
            if not video_processado:
                return {
                    "status": "erro",
                    "mensagem": "Falha ao renderizar vídeo"
                }

            # Obter duração original
            duracao_original = await self._obter_duracao(video_path)
            duracao_processada = await self._obter_duracao(video_processado)

            return {
                "status": "sucesso",
                "video_processado": video_processado,
                "transcricao": transcrição_json,
                "edl": edl_json,
                "duracao_original": duracao_original,
                "duracao_processada": duracao_processada,
                "reducao": f"{((1 - duracao_processada/duracao_original)*100):.1f}%"
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": str(e)
            }

    async def analyze_video(self, video_path: str, edit_dir: str) -> Dict[str, Any]:
        """
        Analisa vídeo e gera visualização timeline

        Returns:
            {
                "status": "sucesso/erro",
                "transcricao": dict,
                "timeline_png": str,  # path para PNG com waveform+filmstrip
                "palavras_chave": list
            }
        """
        try:
            edit_path = Path(edit_dir)
            edit_path.mkdir(parents=True, exist_ok=True)

            # Transcrever
            transcrição_json = await self._transcrever(video_path, edit_dir)
            if not transcrição_json:
                return {
                    "status": "erro",
                    "mensagem": "Falha na transcrição"
                }

            # Gerar timeline visual
            timeline_png = await self._gerar_timeline(video_path, 0, 30, edit_dir)

            # Extrair palavras-chave
            palavras_chave = await self._extrair_palavras_chave(transcrição_json)

            return {
                "status": "sucesso",
                "transcricao": transcrição_json,
                "timeline_png": timeline_png,
                "palavras_chave": palavras_chave
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": str(e)
            }

    # ===== MÉTODOS PRIVADOS =====

    async def _transcrever(self, video_path: str, edit_dir: str) -> Optional[Dict]:
        """Transcrever usando ElevenLabs Scribe via helpers/transcribe.py"""
        try:
            cmd = [
                sys.executable,
                str(self.helpers_path / "transcribe.py"),
                video_path
            ]

            env = os.environ.copy()
            env["ELEVENLABS_API_KEY"] = ELEVENLABS_API_KEY

            result = subprocess.run(
                cmd,
                cwd=str(self.video_use_path),
                capture_output=True,
                text=True,
                timeout=300,
                env=env
            )

            if result.returncode == 0:
                # Arquivo de transcrição deve estar em edit_dir/transcripts/
                transcript_file = Path(edit_dir) / "transcripts" / f"{Path(video_path).stem}.json"
                if transcript_file.exists():
                    with open(transcript_file) as f:
                        return json.load(f)

            print(f"Erro na transcrição: {result.stderr}", file=sys.stderr)
            return None

        except Exception as e:
            print(f"Exceção em _transcrever: {e}", file=sys.stderr)
            return None

    async def _agrupar_transcricao(self, edit_dir: str) -> bool:
        """Agrupar transcrição em takes usando pack_transcripts.py"""
        try:
            cmd = [
                sys.executable,
                str(self.helpers_path / "pack_transcripts.py"),
                "--edit-dir",
                edit_dir
            ]

            result = subprocess.run(
                cmd,
                cwd=str(self.video_use_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Exceção em _agrupar_transcricao: {e}", file=sys.stderr)
            return False

    async def _gerar_edl(self, video_path: str, transcricao: Dict, edit_dir: str) -> Optional[Dict]:
        """
        Gera EDL removendo silêncios baseado na transcrição

        Implementação simplificada que cria EDL com ranges sem silêncios
        """
        try:
            edl = {
                "version": 1,
                "sources": {
                    "C0": video_path
                },
                "ranges": [],
                "total_duration_s": 0.0
            }

            # Extrair informações de palavras da transcrição
            if "words" in transcricao:
                words = transcricao["words"]

                # Agrupar palavras em ranges, pulando grandes silêncios
                current_range_start = None
                silence_threshold = 0.5  # segundos

                for i, word in enumerate(words):
                    start = word.get("start", 0)
                    end = word.get("end", 0)

                    if current_range_start is None:
                        current_range_start = start

                    # Verificar se há grande silêncio até próxima palavra
                    if i < len(words) - 1:
                        next_word_start = words[i + 1].get("start", 0)
                        gap = next_word_start - end

                        if gap > silence_threshold:
                            # Fim do range
                            edl["ranges"].append({
                                "source": "C0",
                                "start": current_range_start,
                                "end": end,
                                "beat": "MAIN"
                            })
                            current_range_start = None
                    else:
                        # Última palavra
                        edl["ranges"].append({
                            "source": "C0",
                            "start": current_range_start,
                            "end": end,
                            "beat": "MAIN"
                        })

                # Calcular duração total
                edl["total_duration_s"] = sum(r["end"] - r["start"] for r in edl["ranges"])

            # Salvar EDL
            edl_path = Path(edit_dir) / "edl.json"
            with open(edl_path, 'w') as f:
                json.dump(edl, f, indent=2)

            return edl

        except Exception as e:
            print(f"Exceção em _gerar_edl: {e}", file=sys.stderr)
            return None

    async def _renderizar(self, edl: Dict, edit_dir: str) -> Optional[str]:
        """Renderizar usando render.py"""
        try:
            edl_path = Path(edit_dir) / "edl.json"
            output_path = Path(edit_dir) / "video_processado.mp4"

            cmd = [
                sys.executable,
                str(self.helpers_path / "render.py"),
                str(edl_path),
                "-o",
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                cwd=str(self.video_use_path),
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0 and output_path.exists():
                return str(output_path)

            print(f"Erro na renderização: {result.stderr}", file=sys.stderr)
            return None

        except Exception as e:
            print(f"Exceção em _renderizar: {e}", file=sys.stderr)
            return None

    async def _gerar_timeline(self, video_path: str, start: float, end: float, edit_dir: str) -> Optional[str]:
        """Gerar PNG com timeline usando timeline_view.py"""
        try:
            output_path = Path(edit_dir) / "timeline.png"

            cmd = [
                sys.executable,
                str(self.helpers_path / "timeline_view.py"),
                video_path,
                str(start),
                str(end),
                "-o",
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                cwd=str(self.video_use_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and output_path.exists():
                return str(output_path)

            return None

        except Exception as e:
            print(f"Exceção em _gerar_timeline: {e}", file=sys.stderr)
            return None

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

    async def _extrair_palavras_chave(self, transcricao: Dict) -> list:
        """Extrair palavras-chave da transcrição (palavras mais frequentes)"""
        try:
            if "text" not in transcricao:
                return []

            text = transcricao["text"].lower()
            # Remover pontuação
            import re
            palavras = re.findall(r'\b\w+\b', text)

            # Filtrar stop words comuns (versão simplificada)
            stop_words = {
                'um', 'uma', 'o', 'a', 'os', 'as', 'de', 'da', 'do', 'das', 'dos',
                'e', 'ou', 'mas', 'que', 'é', 'em', 'para', 'por', 'com', 'sem'
            }

            palavras_relevantes = [p for p in palavras if p not in stop_words and len(p) > 2]

            # Contar frequência e retornar top 10
            from collections import Counter
            freq = Counter(palavras_relevantes)
            return [p for p, _ in freq.most_common(10)]

        except Exception:
            return []
