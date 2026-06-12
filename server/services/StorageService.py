import os
import uuid
from repository.KG_DB import Neo4jGraphDB
from repository.Vector_DB import VectorDB
from services.graph_utils.EntityRelationExtractor import EntityRelationExtractor

class StorageService:
    def __init__(self, kg_db, vector_db, extractor):
        self.kg_db = kg_db
        self.vector_db = vector_db
        self.extractor = extractor

    def process_file(self, file_path_or_text: str):
        """
        Orchestrates full GraphRAG ingestion:
        1. Parse file (or raw text) into text chunks
        2. Embed chunks to ChromaDB
        3. Extract Knowledge Graph from chunks
        4. Save Knowledge Graph to Neo4j
        """
        print(f"Starting ingestion for: {file_path_or_text[:50]}...")
        
        # 1. Translate file to text chunks and media paths
        extraction = self.extractor.translate_to_text(file_path_or_text)
        text_chunks = extraction["text"]
        media_chunks = extraction["media"]
        
        if not text_chunks and not media_chunks:
            print("No text/data extracted. Aborting.")
            return {"status": "error", "message": "No data extracted."}

        # 2. Vector DB Storage
        print("Storing chunks in Vector Database...")
        
        is_file = len(file_path_or_text) < 255 and os.path.isfile(file_path_or_text)
        source_label = file_path_or_text if is_file else "raw_text_upload"
        
        chunks_to_store = []
        metadatas = []
        
        for idx, txt in enumerate(text_chunks):
            chunks_to_store.append(txt)
            metadatas.append({"source": source_label, "source_type": "text", "chunk_idx": idx})
            
        for img_path in media_chunks:
            chunks_to_store.append(img_path)
            metadatas.append({"source": img_path, "source_type": "image", "chunk_idx": 0})
            
        ids = [str(uuid.uuid4()) for _ in chunks_to_store]
        self.vector_db.insert_chunks(chunks_to_store, metadatas, ids)
        
        # 3. Knowledge Graph Extraction
        print("Extracting Knowledge Graph Entities & Relationships...")
        kg = self.extractor.extract_graph(file_path_or_text, text_chunks=text_chunks)
        
        # 4. Graph DB Storage
        print("Merging Graph into Neo4j...")
        self.kg_db.insert_graph(kg)
        
        print("Ingestion Complete!")
        return {
            "status": "success",
            "chunks_stored": len(chunks_to_store), 
            "nodes_extracted": len(kg.nodes), 
            "edges_extracted": len(kg.edges)
        }
