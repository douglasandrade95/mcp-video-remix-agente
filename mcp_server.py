#!/usr/bin/env python3
"""
HTTP Server simples para servir a página HTML
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = int(os.environ.get('PORT', 8000))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}", flush=True)

# Mudar para o diretório correto
os.chdir(Path(__file__).parent)

print(f"🚀 Servidor iniciando na porta {PORT}...")
print(f"📍 Acesse: http://localhost:{PORT}", flush=True)

# Criar servidor
try:
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Servidor rodando! Abra: http://localhost:{PORT}", flush=True)
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\n❌ Servidor parado.", flush=True)
except Exception as e:
    print(f"❌ Erro: {e}", flush=True)
