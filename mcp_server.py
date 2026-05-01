#!/usr/bin/env python3
"""
MCP Server para Agente Remixador de Vídeos
Integra Claude + Freepik + FFmpeg
"""

import json
import sys
import asyncio
from typing import Any

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    ToolCall,
    ToolResult,
    CallToolRequest,
)

from config import CLAUDE_API_KEY, FREEPIK_API_KEY
from handlers.analyzer import VideoAnalyzer
from handlers.freepik_handler import FreepikHandler
from handlers.ffmpeg_handler import FFmpegHandler

# ===== INICIALIZAR SERVER =====
server = Server("mcp-video-remix")

# ===== HANDLERS =====
analyzer = VideoAnalyzer()
freepik = FreepikHandler()
ffmpeg = FFmpegHandler()

# ===== REGISTRAR TOOLS =====

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Lista as ferramentas disponíveis"""
    return [
        Tool(
            name="analisar_video",
            description="Analisa um vídeo de referência e extrai gramática cinematográfica",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Caminho do vídeo de referência"
                    },
                    "conceito": {
                        "type": "string",
                        "description": "Descrição do conceito desejado"
                    }
                },
                "required": ["video_path", "conceito"]
            }
        ),
        Tool(
            name="gerar_prompts",
            description="Gera prompts otimizados para Freepik baseado na análise",
            inputSchema={
                "type": "object",
                "properties": {
                    "grammar": {
                        "type": "object",
                        "description": "Gramática cinematográfica (resultado da análise)"
                    },
                    "conceito": {
                        "type": "string",
                        "description": "Conceito do vídeo"
                    }
                },
                "required": ["grammar", "conceito"]
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
        ),
        Tool(
            name="montar_video_final",
            description="Monta o vídeo final com FFmpeg",
            inputSchema={
                "type": "object",
                "properties": {
                    "videos": {
                        "type": "array",
                        "description": "Lista de caminhos dos vídeos"
                    },
                    "audio": {
                        "type": "string",
                        "description": "Caminho do arquivo de áudio"
                    }
                },
                "required": ["videos"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Executa as ferramentas solicitadas"""
    
    try:
        if name == "analisar_video":
            result = await analyzer.analisar(
                arguments["video_path"],
                arguments["conceito"]
            )
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "gerar_prompts":
            result = await analyzer.gerar_prompts(
                arguments["grammar"],
                arguments["conceito"]
            )
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "gerar_imagens_freepik":
            result = await freepik.gerar_imagens(arguments["prompts"])
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "gerar_videos_freepik":
            result = await freepik.gerar_videos(arguments["prompts"])
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "montar_video_final":
            result = await ffmpeg.montar(
                arguments["videos"],
                arguments.get("audio")
            )
            return [TextContent(type="text", text=json.dumps(result))]
        
        else:
            return [TextContent(
                type="text",
                text=f"Ferramenta '{name}' não encontrada"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Erro: {str(e)}"
        )]

# ===== INICIAR SERVER =====
async def main():
    async with stdio_server(server) as streams:
        await streams[0].awrite(
            json.dumps({"jsonrpc": "2.0", "id": 1, "result": {}})
        )
        print("MCP Server iniciado!", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
