import uuid

from config.rag_config import get_local_embedding, habit_vector_collection


async def sync_log_to_vector_store(text_content: str, user_id: str, habit_id: int = None):
    """
    Converts a free-form text note into a vector and stores it securely in ChromaDB
    tagged with the active user's ID for absolute isolation.
    """
    try:
        # 1. Generate the semantic mathematical vector
        vector = get_local_embedding(text_content)

        # 2. Generate a unique ID for this vector entry
        unique_id = str(uuid.uuid4())

        # 3. Build your multi-tenant metadata filter parameters
        metadata = {"user_id": str(user_id)}
        if habit_id:
            metadata["habit_id"] = int(habit_id)

        # 4. Insert directly into your local ChromaDB collection
        habit_vector_collection.add(
            ids=[unique_id], embeddings=[vector], documents=[text_content], metadatas=[metadata]
        )
        print(f"[RAG Ingestion] Successfully vectorized: '{text_content[:30]}...' for User: {user_id}")
    except Exception as e:
        print(f"[RAG Ingestion Error] Failed to store vector context: {str(e)}")


async def query_user_history_rag(query_text: str, user_id: str, n_results: int = 3) -> str:
    """
    Queries the local ChromaDB vector store for past habit or note entries
    that match the semantic meaning of the user's prompt.

    Guarantees absolute multi-tenant data isolation via metadata pre-filtering.
    """
    try:
        # 1. Convert the user's search text into a query vector string
        query_vector = get_local_embedding(query_text)

        # 2. Execute a metadata-filtered query against your local collection
        results = habit_vector_collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where={"user_id": str(user_id)},  # Strict multi-tenant security shield!
        )

        # 3. Clean and parse the matching documents into a single text block
        documents = results.get("documents", [[]])[0]

        if not documents:
            return "No historical context found matching this topic in their logs."

        context_block = ["--- RELEVANT PAST HISTORICAL LOG NOTES ---"]
        for idx, doc in enumerate(documents, start=1):
            context_block.append(f"[{idx}] {doc}")

        return "\n".join(context_block)

    except Exception as e:
        print(f"[RAG Retrieval Error] Failed to query vector database: {str(e)}")
        return "Error loading historical data records."
