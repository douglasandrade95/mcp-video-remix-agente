#!/usr/bin/env python3
"""
MCP Server para Agente Remixador de Vídeos
Integra Video Use + Hyperframes para edição automática de vídeos
"""

import json
import sys
import asyncio
from typing import Any
from pathlib import Path
import tempfile
import shutil

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from config import WORKSPACE_DIR
from handlers.video_use_handler import VideoUseHandler
from handlers.hyperframes_handler import HyperframesHandler
from handlers.freepik_handler import FreepikHandler

# ===== INICIALIZAR SERVER =====
server = Server("mcp-video-remix")

# ===== HANDLERS =====
video_use = VideoUseHandler()
hyperframes = HyperframesHandler()
freepik = FreepikHandler()

# ===== REGISTRAR TOOLS =====

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lista as ferramentas disponíveis"""
    return [
        Tool(
            name="editar_video",
            description="Edita um vídeo removendo silêncios e adicionando animações sincronizadas",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Caminho do arquivo de vídeo para editar"
                    },
                    "estilo_animacao": {
                        "type": "string",
                        "enum": ["minimal", "vibrant", "cinematic"],
                        "description": "Estilo das animações (padrão: minimal)"
                    },
                    "remover_silencio": {
                        "type": "boolean",
                        "description": "Se deve remover silêncios (padrão: true)"
                    }
                },
                "required": ["video_path"]
            }
        ),
        Tool(
            name="processar_video_use",
            description="Processa um vídeo com Video Use para remover silêncios e repetições",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Caminho do arquivo de vídeo"
                    }
                },
                "required": ["video_path"]
            }
        ),
        Tool(
            name="analisar_video",
            description="Analisa um vídeo e extrai transcrição com timeline visual",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Caminho do arquivo de vídeo"
                    }
                },
                "required": ["video_path"]
            }
        ),
        Tool(
            name="gerar_animacoes",
            description="Gera animações sincronizadas com áudio a partir de uma transcrição",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Caminho do vídeo processado"
                    },
                    "transcricao_path": {
                        "type": "string",
                        "description": "Caminho do arquivo JSON com transcrição"
                    },
                    "estilo": {
                        "type": "string",
                        "enum": ["minimal", "vibrant", "cinematic"],
                        "description": "Estilo das animações"
                    }
                },
                "required": ["video_path", "transcricao_path", "estilo"]
            }
        ),
        Tool(
            name="gerar_imagens_freepik",
            description="Gera imagens usando Freepik API",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompts": {
                        "type": "array",
                        "description": "Lista de prompts para gerar imagens"
                    }
                },
                "required": ["prompts"]
            }
        ),
        Tool(
            name="gerar_videos_freepik",
            description="Gera vídeos usando Freepik API",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompts": {
                        "type": "array",
                        "description": "Lista de prompts para gerar vídeos"
                    }
                },
                "required": ["prompts"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Executa as ferramentas solicitadas"""

    try:
        if name == "editar_video":
            result = await _editar_video_completo(
                arguments["video_path"],
                arguments.get("estilo_animacao", "minimal"),
                arguments.get("remover_silencio", True)
            )
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "processar_video_use":
            result = await _processar_video_use(arguments["video_path"])
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "analisar_video":
            result = await _analisar_video(arguments["video_path"])
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "gerar_animacoes":
            result = await _gerar_animacoes(
                arguments["video_path"],
                arguments["transcricao_path"],
                arguments["estilo"]
            )
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "gerar_imagens_freepik":
            result = await freepik.gerar_imagens(arguments["prompts"])
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "gerar_videos_freepik":
            result = await freepik.gerar_videos(arguments["prompts"])
            return [TextContent(type="text", text=json.dumps(result))]

        else:
            return [TextContent(
                type="text",
                text=f"Ferramenta '{name}' não encontrada"
            )]

    except Exception as e:
        print(f"Erro em {name}: {str(e)}", file=sys.stderr)
        return [TextContent(
            type="text",
            text=f"Erro: {str(e)}"
        )]

# ===== FUNÇÕES AUXILIARES =====

async def _editar_video_completo(
    video_path: str,
    estilo_animacao: str = "minimal",
    remover_silencio: bool = True
) -> dict:
    """Orquestra o fluxo completo: Video Use → Hyperframes"""

    # Criar diretório de trabalho
    workspace = Path(WORKSPACE_DIR) / Path(video_path).stem
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        result = {"status": "processando", "etapas": []}

        # Etapa 1: Processar com Video Use
        if remover_silencio:
            result["etapas"].append("Removendo silêncios com Video Use...")
            vu_result = await video_use.process_video(video_path, str(workspace))

            if vu_result["status"] != "sucesso":
                return {
                    "status": "erro",
                    "mensagem": "Falha ao processar com Video Use",
                    "detalhes": vu_result
                }

            video_processado = vu_result["video_processado"]
            transcricao = vu_result["transcricao"]
            result["etapas"].append(f"✓ Silêncios removidos ({vu_result['reducao']})")
        else:
            video_processado = video_path
            # Análise de vídeo para obter transcrição
            análise = await video_use.analyze_video(video_path, str(workspace))
            if análise["status"] == "sucesso":
                transcricao = análise["transcricao"]
            else:
                transcricao = {}

        # Etapa 2: Gerar animações com Hyperframes
        result["etapas"].append("Gerando animações sincronizadas...")
        anim_result = await hyperframes.generate_animations(
            video_processado,
            transcricao,
            str(workspace),
            estilo_animacao
        )

        if anim_result["status"] != "sucesso":
            return {
                "status": "erro",
                "mensagem": "Falha ao gerar animações",
                "detalhes": anim_result
            }

        result["etapas"].append("✓ Animações geradas")

        # Etapa 3: Renderizar com Hyperframes
        result["etapas"].append("Renderizando vídeo final...")
        render_result = await hyperframes.render_with_animations(
            anim_result["html_path"],
            video_processado,
            str(workspace)
        )

        if render_result["status"] != "sucesso":
            return {
                "status": "erro",
                "mensagem": "Falha ao renderizar vídeo final",
                "detalhes": render_result
            }

        result["etapas"].append("✓ Vídeo final renderizado")

        return {
            "status": "sucesso",
            "video_final": render_result["video_final"],
            "duracao_final": render_result["duracao"],
            "fps": render_result["fps"],
            "workspace": str(workspace),
            "etapas": result["etapas"]
        }

    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro durante processamento: {str(e)}",
            "workspace": str(workspace)
        }

async def _processar_video_use(video_path: str) -> dict:
    """Processa vídeo apenas com Video Use"""
    workspace = Path(WORKSPACE_DIR) / f"{Path(video_path).stem}_vu"
    workspace.mkdir(parents=True, exist_ok=True)

    result = await video_use.process_video(video_path, str(workspace))
    result["workspace"] = str(workspace)
    return result

async def _analisar_video(video_path: str) -> dict:
    """Analisa vídeo para extrair transcrição e metadados"""
    workspace = Path(WORKSPACE_DIR) / f"{Path(video_path).stem}_analysis"
    workspace.mkdir(parents=True, exist_ok=True)

    result = await video_use.analyze_video(video_path, str(workspace))
    result["workspace"] = str(workspace)
    return result

async def _gerar_animacoes(
    video_path: str,
    transcricao_path: str,
    estilo: str = "minimal"
) -> dict:
    """Gera animações baseado em transcrição"""
    workspace = Path(WORKSPACE_DIR) / f"{Path(video_path).stem}_anim"
    workspace.mkdir(parents=True, exist_ok=True)

    # Carregar transcrição
    try:
        with open(transcricao_path) as f:
            transcricao = json.load(f)
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Não foi possível carregar transcrição: {str(e)}"
        }

    result = await hyperframes.generate_animations(
        video_path,
        transcricao,
        str(workspace),
        estilo
    )
    result["workspace"] = str(workspace)
    return result

# ===== INICIAR SERVER =====
async def main():
    async with stdio_server(server) as streams:
        await streams[0].awrite(
            json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}})
        )
        print("MCP Server iniciado!", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
