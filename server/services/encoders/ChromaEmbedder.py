import numpy as np
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from .Encoder import Encoder

class ChromaEmbedder(EmbeddingFunction):
    """
    Custom embedding function for ChromaDB that uses the universal Encoder.
    It processes standard text strings as well as file paths to PDFs, images, audio, and video.
    """
    def __init__(self, device="cuda"):
        self.encoder = Encoder(device)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            # We assume doc could be a string text or a valid file path.
            result = self.encoder.encode(doc)
            
            # Collect all embeddings across all modalities (text, image, audio, video)
            all_embeddings = []
            
            for modality, embs in result.items():
                if isinstance(embs, np.ndarray):
                    if len(embs.shape) == 2:
                        # Append each chunk's embedding
                        all_embeddings.extend([e for e in embs])
                    else:
                        all_embeddings.append(embs)
                elif isinstance(embs, list):
                    # For lists of numpy arrays (e.g., PDF image_embeddings)
                    for e in embs:
                        if isinstance(e, np.ndarray):
                            if len(e.shape) == 2:
                                all_embeddings.extend([chunk_e for chunk_e in e])
                            else:
                                all_embeddings.append(e)

            # Pool all collected embeddings into a single unified document vector
            if len(all_embeddings) > 0:
                stacked_embs = np.stack(all_embeddings)
                pooled_emb = stacked_embs.mean(axis=0)
                
                # Re-normalize to unit sphere
                norm = np.linalg.norm(pooled_emb)
                if norm > 0:
                    pooled_emb = pooled_emb / norm
                    
                emb = pooled_emb.tolist()
            else:
                emb = []
                
            embeddings.append(emb)
            
        return embeddings
