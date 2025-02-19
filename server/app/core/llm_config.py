from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMSettings(BaseSettings):
    DATA_DIR: str = "data"
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    VECTOR_DB_PATH: str = "faiss_index"
    LLM_MODEL: str = "deepseek-r1:8b"
    TEMPERATURE: float = 0.3
    NUM_CTX: int = 4096
    NUM_GPU: int = 1
    TOP_K: int = 3

    model_config = SettingsConfigDict(case_sensitive=True)

llm_settings = LLMSettings() 