#!/usr/bin/env python3
"""
HTTP Server para edição de vídeos
Integra Video Use + Hyperframes via página web
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = int(os.environ.get('PORT', 8000))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

# Mudar para o diretório correto
os.chdir(Path(__file__).parent)

# Criar servidor
with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
    print(f"✓ Servidor rodando em http://0.0.0.0:{PORT}", flush=True)
    print(f"✓ Acesse: http://localhost:{PORT}", flush=True)
    httpd.serve_forever()
