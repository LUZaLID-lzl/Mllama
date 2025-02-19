from pydantic_settings import BaseSettings, SettingsConfigDict

class ServerSettings(BaseSettings):
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    WORKERS: int = 1
    
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "认证知识库系统"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "认证知识库系统API"
    
    # CORS配置
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]

    # 数据和模型配置
    DATA_DIR: str = "data"
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    VECTOR_DB_PATH: str = "faiss_index"
    LLM_MODEL: str = "deepseek-r1:8b"
    TEMPERATURE: float = 0.3
    NUM_CTX: int = 4096
    NUM_GPU: int = 1
    TOP_K: int = 3

    model_config = SettingsConfigDict(case_sensitive=True)

server_settings = ServerSettings() 