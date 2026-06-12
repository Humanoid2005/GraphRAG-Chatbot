from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from controller.GraphController import router as graph_router
from repository.KG_DB import Neo4jGraphDB
from repository.Vector_DB import VectorDB
from services.graph_utils.EntityRelationExtractor import EntityRelationExtractor

@asynccontextmanager
async def lifespan(app):
    # Startup code
    print("Starting up GraphRAG engine...")
    app.state.kg_db = Neo4jGraphDB()
    app.state.vector_db = VectorDB()
    app.state.extractor = EntityRelationExtractor()
    yield
    # Shutdown code
    print("Shutting down the application...")
    if hasattr(app.state, 'kg_db'):
        app.state.kg_db.close()

app = FastAPI(lifespan=lifespan, title="GraphRAG Multimodal API")

app.include_router(graph_router)

@app.get("/")
async def root():
    return {"message": "GraphRAG API is running. Ready for /api/upload and /api/query."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)