import os
from ollama import Client
from repository.KG_DB import Neo4jGraphDB
from repository.Vector_DB import VectorDB
from config.Config import (
    OLLAMA_BASE_URL, 
    OLLAMA_MODEL, 
    OLLAMA_GENERATION_MODEL,
    OLLAMA_VISION_MODEL,
    VECTOR_SEARCH_TOP_K,
    GRAPH_SEARCH_MAX_DEPTH,
    GRAPH_SEARCH_LIMIT
)

class RetrievalService:
    def __init__(self, kg_db, vector_db):
        self.kg_db = kg_db
        self.vector_db = vector_db
        self.ollama_client = Client(host=OLLAMA_BASE_URL)
        self.extraction_model = OLLAMA_MODEL
        self.generation_model = OLLAMA_GENERATION_MODEL

    def _extract_query_entities(self, query: str) -> list[str]:
        """Uses a fast LLM call to extract entity names from the user's question."""
        prompt = f"Extract the core entities/subjects from the following question. Output a simple comma separated list of names only. Question: {query}"
        try:
            response = self.ollama_client.chat(
                model=self.generation_model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.0}
            )
            entities_str = response['message']['content']
            # Split by comma and clean up
            entities = [e.strip() for e in entities_str.split(',') if e.strip()]
            return entities
        except Exception as e:
            print(f"Failed to extract entities from query: {e}")
            return []

    def answer_question(self, query: str) -> dict:
        """
        The Core GraphRAG Loop:
        1. Semantic Search (ChromaDB)
        2. Graph Search (Neo4j)
        3. LLM Synthesis
        """
        print(f"Processing Query: {query}")
        
        # 1. Semantic Search
        print("Retrieving Semantic Context...")
        semantic_results = self.vector_db.search(query, n_results=VECTOR_SEARCH_TOP_K)
        semantic_chunks = [res['document'] for res in semantic_results]
        semantic_context = "\n---\n".join(semantic_chunks) if semantic_chunks else "No direct textual matches found."
        
        # Check for physical images in retrieved chunks
        image_paths = []
        for res in semantic_results:
            if res.get('metadata', {}).get('source_type') == 'image':
                img_path = res['metadata'].get('source')
                if img_path and img_path not in image_paths:
                    if os.path.exists(img_path):
                        image_paths.append(img_path)
        
        # 2. Graph Search
        print("Extracting Graph Entities...")
        query_entities = self._extract_query_entities(query)
        graph_relationships = []
        causal_chains = []
        if query_entities:
            print(f"Querying Neo4j for entities: {query_entities}")
            graph_relationships = self.kg_db.get_subgraph(query_entities, limit=GRAPH_SEARCH_LIMIT)
            print("Tracing Multi-Hop Causal Chains...")
            causal_chains = self.kg_db.get_causal_chain(query_entities, max_depth=GRAPH_SEARCH_MAX_DEPTH, limit=GRAPH_SEARCH_LIMIT)
            
        graph_context = "\n".join(graph_relationships) if graph_relationships else "No generic graph relationships found."
        causal_context = "\n".join(causal_chains) if causal_chains else "No multi-hop causal chains found."
        
        # 3. LLM Synthesis
        print("Synthesizing Final Answer...")
        final_prompt = f"""
You are an expert Question Answering system using a Causal GraphRAG architecture.
You have been provided with Semantic Context (direct text chunks), Graph Context (entity relationships), and Causal Chains (domino-effects over multiple hops).
Answer the user's question using ONLY the provided context. Pay special attention to the causal chains to predict consequences or trace root causes.

User Question: {query}

### Semantic Context (Vector Match):
{semantic_context}

### Graph Context (Neo4j Match):
{graph_context}

### Causal Chains (Multi-Hop Neo4j Match):
{causal_context}

Provide a comprehensive and detailed answer utilizing the text excerpts, graph relationships, and explicit tracing of the causal domino effects if relevant.
"""
        model_to_use = self.generation_model
        images_for_prompt = []
        
        if image_paths:
            print(f"Detected {len(image_paths)} images in context! Switching to Vision Model: {OLLAMA_VISION_MODEL}")
            model_to_use = OLLAMA_VISION_MODEL
            for img_path in image_paths:
                try:
                    with open(img_path, "rb") as f:
                        images_for_prompt.append(f.read())
                except Exception as e:
                    print(f"Failed to load image bytes for {img_path}: {e}")

        message_payload = {'role': 'user', 'content': final_prompt}
        if images_for_prompt:
            message_payload['images'] = images_for_prompt
            
        response = self.ollama_client.chat(
            model=model_to_use,
            messages=[message_payload]
        )
        return {
            "answer": response['message']['content'],
            "context": {
                "vector_chunks": semantic_chunks,
                "vector_images": image_paths,
                "graph_relationships": graph_relationships,
                "causal_chains": causal_chains
            }
        }
