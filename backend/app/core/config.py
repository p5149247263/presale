from pydantic_settings import BaseSettings, SettingsConfigDict
import os


def _default_data_root() -> str:
    # Vercel/serverless runtime supports ephemeral writes under /tmp.
    if os.getenv("VERCEL"):
        return "/tmp/ai-presales-copilot"
    return "app/data"


DATA_ROOT = _default_data_root()
DEFAULT_STORAGE_PATH = f"{DATA_ROOT}/storage"
DEFAULT_OUTPUT_PATH = f"{DATA_ROOT}/output"
DEFAULT_AUDIT_LOG_PATH = f"{DATA_ROOT}/audit.log"


class Settings(BaseSettings):
    app_name: str = "AI Presales Copilot"
    env: str = "dev"
    storage_path: str = DEFAULT_STORAGE_PATH
    output_path: str = DEFAULT_OUTPUT_PATH
    audit_log_path: str = DEFAULT_AUDIT_LOG_PATH
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
