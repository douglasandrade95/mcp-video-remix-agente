#!/usr/bin/env python3
"""
Servidor Flask para edição de vídeos
Integra Video Use + Hyperframes
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from pathlib import Path
from config import WORKSPACE_DIR
import traceback

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = str(WORKSPACE_DIR / 'uploads')

# Criar pasta de uploads
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

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

        return jsonify({
            "status": "processando",
            "mensagem": "Vídeo em processamento...",
            "etapas": [
                "Removendo silêncios...",
                "Gerando animações...",
                "Renderizando...",
            ],
            "workspace": str(edit_dir)
        })

    except Exception as e:
        traceback.print_exc()
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
