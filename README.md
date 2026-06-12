# GraphRAG Nexus

GraphRAG Nexus is a cutting-edge Retrieval-Augmented Generation (RAG) system that integrates vector semantics with explicit knowledge graphs. By combining dense semantic similarity search with topological graph traversals, this system enables deep, multi-hop reasoning over complex documents, images, and audio files.

## Architecture Overview

The system operates on a dual-retrieval architecture:
1. **Vector Store (ChromaDB)**: Handles dense embeddings for rapid, similarity-based retrieval of raw text chunks and visual analysis descriptions.
2. **Knowledge Graph (Neo4j)**: Maps entities, relationships, and causal chains to preserve the structural and logical context of the ingested data.

When a query is made, the `GraphController` and `RetrievalService` orchestrate a parallel search across both databases, feeding the LLM a highly contextualized prompt that eliminates hallucinations on complex, multi-hop questions.

### Key Capabilities
- **Multi-Modal Ingestion**: Upload documents, images, or record raw audio directly through the UI.
- **Multi-Hop Reasoning**: Leverages causal chains to understand "A causes B, which triggers C."
- **Agency-Grade UI**: A premium, "Doppelrand" (Double-Bezel) glassmorphic React frontend featuring Framer Motion physics and dynamic Light/Dark themes.

---

## Tech Stack

### Frontend (Client)
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS + Custom Glassmorphism UI Tokens
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Markdown Rendering**: `react-markdown` + `remark-gfm`
- **Features**: Real-time voice recording (MediaRecorder API), Native Dark Mode, Responsive Layouts.

### Backend (Server)
- **Language**: Python (Port 8000)
- **Graph Database**: Neo4j
- **Vector Database**: ChromaDB
- **Endpoints**: `/api/query` (for text inference) and `/api/upload` (for multi-modal data ingestion).

##  Custom Finetuning (Notebooks)
The project includes specialized Jupyter notebooks in the `notebooks/` directory for enhancing both the vector and graph components of the pipeline:

1. **Knowledge Graph Extractor Finetuning (`finetune-sciphy-triplex.ipynb`)**
   - **Task**: Trains a local LLM to accurately extract topological entities and relationships (Nodes and Edges) from unstructured text into a strict JSON schema.
   - **Method**: Parameter-Efficient Fine-Tuning (PEFT) using Unsloth with 4-bit quantized LoRA adapters on a base Llama 3 model.
   - **Dataset**: `Jotschi/wikipedia_knowledge_graph_en`. Streaming a subset of **25,000 samples** out of the **17 Million** total available rows.

2. **Embedding Alignment & Distillation (`grag-embeddingfinetuning.ipynb`)**
   - **Task**: Aligns a lightweight, highly efficient student text embedding model to a larger multi-modal teacher model. This optimizes the semantic search within the ChromaDB vector database.
   - **Method**: Trains a custom bottleneck Projection MLP head to minimize the Cosine Similarity Loss between the student (`nomic-embed-text-v1.5`) and teacher (`clip-vit-large-patch14`) embeddings.
   - **Dataset**: Cornell University arXiv metadata snapshot. Extracted and filtered exactly **2,000,000 samples** based on strict CLIP token-count boundaries.

###  Performance & Training Metrics
The following scoring metrics were achieved during the finetuning phases:

- **KG Extractor (Llama-3 8B LoRA)**: 
  - **Final Training Loss**: `~0.42` (Converged after 600 steps).
  - **Schema Adherence**: `100%` (Model successfully learned to output strict JSON without markdown wrappers).
  - **Entity/Relation Extraction Precision (Estimated)**: `~89%` on the held-out validation set.
  - **Trainable Parameters**: ~41.9 Million (0.52% of total via LoRA).

- **Embedding Alignment (Nomic-to-CLIP)**:
  - **Final Cosine Loss**: Converged to `~0.15`.
  - **Teacher-Student Similarity**: Achieved an average cosine similarity of `0.85` relative to the CLIP-ViT-Large teacher embeddings.
  - **Throughput**: Processed 2M samples simultaneously at a batch size of 512, completely eliminating tokenization bottlenecks.

*(Note: End-to-end GraphRAG evaluation metrics like **Faithfulness**, **Answer Relevance (RAGAS)**, and **Mean Reciprocal Rank (MRR)** for graph traversal paths are actively being benchmarked).*

---

##  Future Improvements (Roadmap)
The following architectural enhancements are planned for future iterations of GraphRAG Nexus:

- **Session-Based Memory Management**: Implementing short-term conversational buffers and long-term user profiles (e.g., using Redis or Neo4j temporal edges) to maintain deep conversational context across multi-turn sessions.
- **Dynamic Ontology Expansion**: Evolving from a fixed schema to an adaptive ontology that automatically infers and creates new node and edge categories based on the organic structure of incoming documents.
- **Hybrid Query Routing**: Building a lightweight intent-classification layer to intelligently route simple factual queries to vector-only search (saving compute) and complex reasoning queries to the full dual-GraphRAG pipeline.
- **Real-Time Token Streaming**: Upgrading the FastAPI backend and React frontend to support Server-Sent Events (SSE), allowing the LLM's response to stream instantly token-by-token.
- **Multi-Agent Ingestion**: Deploying parallel, specialized sub-agents (e.g., Vision agents for charts, Audio agents for transcripts) that asynchronously analyze and populate the Neo4j graph during bulk file uploads.
- **Web-scraping augmented data ingestion**: Use web-scraping APIs or python packages like bs4 and selenium to scrape web information and use that also to augment user query answering.

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- Neo4j Desktop or Neo4j AuraDB instance
- Ollama

### 1. Backend Setup
1. Navigate to the server directory:
   ```bash
   cd server
   ```
2. Install Python dependencies (ensure you have a virtual environment active):
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your server environment variables (Neo4j URI, Chroma paths, API keys in a .env in server folder). The name of configurable variables will be in the Config.py file in the config folder of the server.
4. Start the backend server (typically running on `http://127.0.0.1:8000`):
   ```bash
   # Adjust based on your specific entry point (e.g., uvicorn main:app --reload)
   python main.py
   ```

### 2. Frontend Setup
1. Navigate to the client directory:
   ```bash
   cd client
   ```
2. Install the required npm packages:
   ```bash
   npm install
   ```
3. Configure your frontend API URL. Ensure your `client/.env` file has:
   ```env
   VITE_BACKEND_URL=http://127.0.0.1:8000
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
5. The application will be available at `http://localhost:5173`.

---
