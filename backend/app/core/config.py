from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Presales Copilot"
    env: str = "dev"
    storage_path: str = "app/data/storage"
    encryption_key: str = ""
    llm_provider: str = "mock"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    local_llm_base_url: str = "http://localhost:11434"
    vector_provider: str = "faiss_local"
    pinecone_api_key: str = ""
    azure_search_endpoint: str = ""
    pii_redaction_enabled: bool = True
    cors_origins: str = "*"
    cors_allow_credentials: bool = False

    model_config = SettingsConfigDict(env_prefix="COPILOT_", env_file=".env", extra="ignore")


settings = Settings()
