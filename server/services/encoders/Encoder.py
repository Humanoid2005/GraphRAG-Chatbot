import os
import torch
from sentence_transformers import SentenceTransformer
from PIL import Image

class Encoder:
    def __init__(self, device="cpu"):
        self.device = device
        
        # Load the unified Jina Omni Nano model (handles text, image, audio, video)
        print("Loading jina-embeddings-v5-omni-nano...")
        self.model = SentenceTransformer("jinaai/jina-embeddings-v5-omni-nano", trust_remote_code=True, device=device)

    def get_type(self, source_path):
        try:
            is_file = isinstance(source_path, str) and os.path.isfile(source_path)
        except Exception:
            is_file = False
            
        if not is_file:
            return "raw_text"

        if "." not in source_path:
            return "raw_text"

        source_type = source_path.split(".")[-1].lower()

        if source_type in ["png","jpg","jpeg","gif","webp"]:
            return "image"
        elif source_type in ["wav","mp3","flac","aac","m4a"]:
            return "audio"
        elif source_type in ["mp4","avi","mkv","mov","wmv"]:
            return "video"
        elif source_type == "txt":
            return "text_file"
        else:
            return "raw_text"

    def encode(self, source_path):
        source_type = self.get_type(source_path)

        if source_type == "image":
            image_embedding = self.model.encode(Image.open(source_path))
            return {"image": image_embedding}

        elif source_type in ["audio", "video"]:
            media_embedding = self.model.encode(source_path)
            return {source_type: media_embedding}
            
        elif source_type == "text_file":
            with open(source_path, "r", encoding="utf-8") as f:
                content = f.read()
            text_embedding = self.model.encode([content])[0]
            return {"text": text_embedding}
            
        else: # raw_text
            text_embedding = self.model.encode([source_path])[0]
            return {"text": text_embedding}
