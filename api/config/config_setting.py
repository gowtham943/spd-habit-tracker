from pydantic_settings import BaseSettings, SettingsConfigDict


class config_setting(BaseSettings):
    DATABASE_URL: str
    DIRECT_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OLLAMA_HOST: str = "http://localhost:11434"
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "all-minilm:v2"
    MCP_SERVER_SSE_URL: str = "http://habit_api:8000/mcp/sse"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = config_setting()
