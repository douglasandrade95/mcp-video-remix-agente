import requests
import time
import json
from config import FREEPIK_API_KEY, FREEPIK_IMAGE_GEN, FREEPIK_VIDEO_GEN

class FreepikHandler:
    def __init__(self):
        self.headers = {
            "X-Freepik-API-Key": FREEPIK_API_KEY,
            "Content-Type": "application/json"
        }
    
    async def gerar_imagens(self, prompts: list) -> dict:
        """Gera imagens no Freepik"""
        imagens = []
        
        for i, prompt_data in enumerate(prompts):
            payload = {
                "prompt": prompt_data.get("prompt", ""),
                "size": "2560x1440",
                "num_images": 1
            }
            
            try:
                response = requests.post(
                    FREEPIK_IMAGE_GEN,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    url = data["data"][0]["url"]
                    imagens.append({
                        "numero": i + 1,
                        "url": url,
                        "status": "sucesso"
                    })
                else:
                    imagens.append({
                        "numero": i + 1,
                        "status": "erro",
                        "codigo": response.status_code
                    })
            except Exception as e:
                imagens.append({
                    "numero": i + 1,
                    "status": "erro",
                    "mensagem": str(e)
                })
            
            time.sleep(2)
        
        return {"imagens": imagens}
    
    async def gerar_videos(self, prompts: list) -> dict:
        """Gera vídeos no Freepik"""
        videos = []
        
        for i, prompt_data in enumerate(prompts):
            payload = {
                "prompt": prompt_data.get("prompt", ""),
                "duration": 3,
                "fps": 24,
                "size": "720x1280"
            }
            
            try:
                response = requests.post(
                    FREEPIK_VIDEO_GEN,
                    headers=self.headers,
                    json=payload,
                    timeout=120
                )
                
                if response.status_code in [200, 202]:
                    data = response.json()
                    task_id = data.get("id")
                    videos.append({
                        "numero": i + 1,
                        "task_id": task_id,
                        "status": "processando"
                    })
                else:
                    videos.append({
                        "numero": i + 1,
                        "status": "erro"
                    })
            except Exception as e:
                videos.append({
                    "numero": i + 1,
                    "status": "erro",
                    "mensagem": str(e)
                })
            
            time.sleep(2)
        
        return {"videos": videos}
