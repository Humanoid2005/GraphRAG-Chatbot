import chromadb
from typing import List, Dict, Any
from services.encoders.ChromaEmbedder import ChromaEmbedder

class VectorDB:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "graphrag_chunks"):
        """Initializes a persistent ChromaDB client and creates the semantic collection."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize our custom multi-modal Jina embedder
        self.embedder = ChromaEmbedder(device="cpu")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedder
        )

    def insert_chunks(self, chunks: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Inserts raw text chunks into ChromaDB."""
        if not chunks:
            return
            
        self.collection.upsert(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Queries the vector database for semantically relevant chunks and their metadata."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        extracted_results = []
        if results and 'documents' in results and len(results['documents']) > 0:
            docs = results['documents'][0]
            metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(docs)
            for doc, meta in zip(docs, metas):
                extracted_results.append({
                    "document": doc,
                    "metadata": meta
                })
        return extracted_results
