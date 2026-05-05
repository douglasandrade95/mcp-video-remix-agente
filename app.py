#!/usr/bin/env python3
"""
Servidor Flask para edição de vídeos
Integra Video Use + Hyperframes
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import asyncio
import threading
from pathlib import Path
from config import WORKSPACE_DIR
from handlers.video_use_handler import VideoUseHandler
from handlers.hyperframes_handler import HyperframesHandler
import traceback

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = str(WORKSPACE_DIR / 'uploads')

# Criar pasta de uploads
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

# Dicionário para rastrear processamento
processing_status = {}

def run_async(coro):
    """Helper para rodar coroutines async em contexto sync"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Se há loop rodando, criar nova tarefa
            future = asyncio.ensure_future(coro)
            return future.result(timeout=600)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # Criar novo loop se não existir
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

def process_video_async(video_path, edit_dir, estilo):
    """Processa vídeo em thread separada"""
    try:
        job_id = str(Path(video_path).stem)
        processing_status[job_id] = {
            "status": "processando",
            "etapa": "Iniciando...",
            "progress": 0
        }

        # Video Use
        processing_status[job_id]["etapa"] = "Removendo silêncios..."
        processing_status[job_id]["progress"] = 10
        video_handler = VideoUseHandler()
        video_result = run_async(
            video_handler.process_video(str(video_path), str(edit_dir))
        )

        if video_result.get("status") != "sucesso":
            processing_status[job_id] = {
                "status": "erro",
                "mensagem": video_result.get("mensagem", "Erro no Video Use"),
                "progress": 0
            }
            return

        video_processado = video_result.get("video_processado")
        transcricao = video_result.get("transcricao", {})

        processing_status[job_id]["etapa"] = "Gerando animações..."
        processing_status[job_id]["progress"] = 50

        # Hyperframes - Gerar animações
        hyperframes_handler = HyperframesHandler()
        anim_result = run_async(
            hyperframes_handler.generate_animations(
                video_processado,
                transcricao,
                str(edit_dir),
                estilo
            )
        )

        if anim_result.get("status") != "sucesso":
            processing_status[job_id] = {
                "status": "erro",
                "mensagem": anim_result.get("mensagem", "Erro ao gerar animações"),
                "progress": 0
            }
            return

        html_path = anim_result.get("html_path")

        processing_status[job_id]["etapa"] = "Renderizando vídeo final..."
        processing_status[job_id]["progress"] = 75

        # Hyperframes - Renderizar
        render_result = run_async(
            hyperframes_handler.render_with_animations(
                html_path,
                video_processado,
                str(edit_dir)
            )
        )

        if render_result.get("status") != "sucesso":
            processing_status[job_id] = {
                "status": "erro",
                "mensagem": render_result.get("mensagem", "Erro ao renderizar"),
                "progress": 0
            }
            return

        video_final = render_result.get("video_final")

        processing_status[job_id] = {
            "status": "sucesso",
            "mensagem": "Vídeo processado com sucesso!",
            "video_final": video_final,
            "video_processado": video_processado,
            "duracao_original": video_result.get("duracao_original"),
            "duracao_processada": video_result.get("duracao_processada"),
            "reducao": video_result.get("reducao"),
            "progress": 100
        }

    except Exception as e:
        traceback.print_exc()
        job_id = str(Path(video_path).stem)
        processing_status[job_id] = {
            "status": "erro",
            "mensagem": str(e),
            "progress": 0
        }

@app.route('/')
def index():
    """Serve a página HTML"""
    return send_file('index.html', mimetype='text/html')

@app.route('/api/health', methods=['GET'])
def health():
    """Verifica saúde do servidor"""
    return jsonify({
        "status": "ok",
        "message": "Servidor funcionando!",
        "workspace": str(WORKSPACE_DIR)
    })

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Recebe upload de vídeo"""
    try:
        if 'video' not in request.files:
            return jsonify({"status": "erro", "mensagem": "Nenhum vídeo enviado"}), 400

        file = request.files['video']
        if file.filename == '':
            return jsonify({"status": "erro", "mensagem": "Arquivo vazio"}), 400

        # Salvar arquivo
        filename = file.filename
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))

        return jsonify({
            "status": "sucesso",
            "mensagem": "Vídeo recebido!",
            "filename": filename,
            "path": str(filepath),
            "size": os.path.getsize(filepath)
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

@app.route('/api/process', methods=['POST'])
def process_video():
    """Processa vídeo com Video Use + Hyperframes"""
    try:
        data = request.json
        filename = data.get('filename')
        estilo = data.get('estilo', 'minimal')

        if not filename:
            return jsonify({"status": "erro", "mensagem": "Filename obrigatório"}), 400

        video_path = Path(app.config['UPLOAD_FOLDER']) / filename
        if not video_path.exists():
            return jsonify({"status": "erro", "mensagem": "Vídeo não encontrado"}), 404

        # Criar workspace para este vídeo
        edit_dir = WORKSPACE_DIR / filename.split('.')[0]
        edit_dir.mkdir(parents=True, exist_ok=True)

        # Iniciar processamento em thread separada
        job_id = str(video_path.stem)
        thread = threading.Thread(
            target=process_video_async,
            args=(str(video_path), str(edit_dir), estilo)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            "status": "processando",
            "job_id": job_id,
            "mensagem": "Vídeo em processamento...",
            "etapas": [
                "Removendo silêncios...",
                "Gerando animações...",
                "Renderizando...",
            ]
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Obtém status do processamento"""
    if job_id in processing_status:
        return jsonify(processing_status[job_id])
    else:
        return jsonify({
            "status": "aguardando",
            "mensagem": "Processamento ainda não iniciado"
        })

@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """Baixa vídeo processado"""
    try:
        if job_id not in processing_status:
            return jsonify({"status": "erro", "mensagem": "Job não encontrado"}), 404

        status = processing_status[job_id]
        if status.get("status") != "sucesso":
            return jsonify({
                "status": "erro",
                "mensagem": "Vídeo ainda não foi processado"
            }), 400

        video_final = status.get("video_final")
        if not Path(video_final).exists():
            return jsonify({
                "status": "erro",
                "mensagem": "Arquivo de vídeo não encontrado"
            }), 404

        return send_file(
            video_final,
            as_attachment=True,
            download_name=f"video_editado_{job_id}.mp4"
        )

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

@app.route('/api/videos', methods=['GET'])
def list_videos():
    """Lista vídeos no workspace"""
    try:
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        videos = []

        if upload_dir.exists():
            for file in upload_dir.glob('*'):
                if file.is_file():
                    videos.append({
                        "name": file.name,
                        "size": file.stat().st_size,
                        "created": str(file.stat().st_mtime)
                    })

        return jsonify({
            "status": "sucesso",
            "videos": videos,
            "total": len(videos)
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Serve index.html para rotas não encontradas"""
    return send_file('index.html', mimetype='text/html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Servidor Flask rodando em http://0.0.0.0:{port}")
    print(f"📍 Acesse: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
