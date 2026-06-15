import chromadb
import ollama

from config.config_setting import settings

# Initialize your explicit Ollama client pointing to the dynamic host network
ollama_client = ollama.Client(host=settings.OLLAMA_HOST)

# 1. Initialize a persistent local directory for ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 2. Get or create a unified collection for your habit logging history
# (ChromaDB handles collections similarly to tables in PostgreSQL)
habit_vector_collection = chroma_client.get_or_create_collection(name="user_habit_history")


def get_local_embedding(text: str) -> list:
    """
    Calls your local Ollama instance to generate an embedding vector for a given text string.
    Uses 'settings.EMBEDDING_MODEL', which is highly efficient on Apple Silicon.
    """
    response = ollama_client.embeddings(model=settings.EMBEDDING_MODEL, prompt=text)
    return response["embedding"]
