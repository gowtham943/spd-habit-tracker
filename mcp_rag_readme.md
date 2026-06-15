# Habit Tracker: AI-Integrated Architecture
This application features a dual-layer AI architecture that combines Model Context Protocol (MCP) for deterministic system actions and Retrieval-Augmented Generation (RAG) for semantic historical analysis.

## System Architecture Overview
The system acts as a "Brain, Hands, and Feet" setup:

The Brain (RAG): Uses a local ChromaDB vector store to search for historical patterns and moods across unstructured chat logs.

The Hands/Feet (MCP): Uses standardized protocol tools to perform precise, authenticated writes to your PostgreSQL database.

### MCP Implementation (Write Layer)
The MCP layer bypasses custom, messy API connectors by exposing your existing SQLAlchemy repositories as standardized tools.

**How it Works**

Transport: We mount an MCP SSE (Server-Sent Events) handler directly into your FastAPI application at /mcp/sse.

Tool Mapping: Functions like create_user_task and log_habit_completion are decorated and exposed as tools.

Authentication: Since AI agents cannot naturally pass browser HTTP headers, we explicitly inject the user_id into the tool context during the agent loop to maintain strict multi-tenancy and prevent data leaks.

Execution: The LLM (Gemini or Ollama) identifies the intent, triggers the tool via JSON-RPC, and FastAPI safely executes the database mutation.

### RAG Implementation (Read Layer)
The RAG layer provides semantic memory, allowing the AI to understand "vague" human queries by referencing past logs.

**How it Works**

Ingestion: Whenever an MCP write operation succeeds (e.g., logging a habit), the system automatically converts the note into a vector embedding using all-minilm:v2 and caches it in ChromaDB, tagged with the user's user_id.


Retrieval: When a user asks a question, the system uses semantic similarity search to find the most relevant past logs.


Isolation: Every search includes a metadata filter (WHERE user_id == active_user_id) to ensure users only ever "remember" their own data.


Synthesis: These relevant snippets are injected into the system prompt, giving the LLM a perfect, context-aware memory to answer complex questions without hallucinating.

# Technical Stack
Backend: FastAPI + SQLAlchemy (Async)


**LLM Orchestration**: Gemini API (or Ollama for local fallback) 


**Protocol**: Model Context Protocol (MCP) via SSE 


**Vector Store**: ChromaDB (Persistent) 


**Embedding Model **: all-minilm:v2 (for 384-dimension vector alignment) 

# Getting Started
To boot the full ecosystem locally:


**Configure**: Ensure your .env_docker contains your GEMINI_API_KEY.


**Flush**: Clear existing volume states to ensure dimensional alignment:

```text
docker compose down -v
Launch:
```

```text
docker compose up --build
```

**Verify**: Check the logs to ensure habit_api has successfully connected to the MCP endpoints and habit_ollama has initialized the embedding model.