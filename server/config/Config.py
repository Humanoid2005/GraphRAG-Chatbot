from starlette.config import Config
from urllib.parse import quote_plus


config = Config(".env")

FRONTEND_URL = config('FRONTEND_URL', default=None)
BACKEND_URL = config('BACKEND_URL', default=None)

# Ollama LLM Configuration
OLLAMA_BASE_URL = config('OLLAMA_BASE_URL', default="http://127.0.0.1:11434")
OLLAMA_MODEL = config('OLLAMA_MODEL', default="sciphi/triplex")
OLLAMA_GENERATION_MODEL = config('OLLAMA_GENERATION_MODEL', default="llama3")
OLLAMA_VISION_MODEL = config('OLLAMA_VISION_MODEL', default="llava-phi3") # Conversational model

# Neo4j Configuration
NEO4J_URI = config('NEO4J_URI', default="neo4j://127.0.0.1:7687")
NEO4J_USERNAME = config('NEO4J_USERNAME', default="neo4j")
NEO4J_PASSWORD = config('NEO4J_PASSWORD', default="password")

# Search Hyperparameters
VECTOR_SEARCH_TOP_K = config('VECTOR_SEARCH_TOP_K', cast=int, default=5)
GRAPH_SEARCH_MAX_DEPTH = config('GRAPH_SEARCH_MAX_DEPTH', cast=int, default=3)
GRAPH_SEARCH_LIMIT = config('GRAPH_SEARCH_LIMIT', cast=int, default=50)

