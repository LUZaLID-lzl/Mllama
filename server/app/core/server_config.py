from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class ServerSettings(BaseSettings):
    """服务器全局配置"""
    
    # 基础服务配置
    HOST: str = "0.0.0.0"  # 服务器监听地址
    PORT: int = 8000       # 服务器端口
    RELOAD: bool = True    # 是否启用热重载
    WORKERS: int = 1       # 工作进程数
    
    # API配置
    API_V1_STR: str = "/api/v1"  # API版本前缀
    PROJECT_NAME: str = "认证知识库系统"  # 项目名称
    VERSION: str = "1.0.0"  # API版本
    DESCRIPTION: str = "认证知识库系统API"  # API描述
    
    # CORS配置
    ALLOW_ORIGINS: List[str] = ["*"]  # 允许的源
    ALLOW_CREDENTIALS: bool = True     # 是否允许携带凭证
    ALLOW_METHODS: List[str] = ["*"]   # 允许的HTTP方法
    ALLOW_HEADERS: List[str] = ["*"]   # 允许的HTTP头

    # 数据目录配置
    DATA_DIR: str = "data"  # 数据文件目录
    CACHE_DIR: str = ".cache"  # 缓存目录
    VECTOR_DB_PATH: str = "faiss_index"  # 向量数据库路径
    
    # Embedding模型配置
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"  # Embedding模型名称
    EMBEDDING_DEVICE: str = "cpu"  # 强制使用 CPU
    EMBEDDING_BATCH_SIZE: int = 32  # Embedding批处理大小
    
    # LLM模型配置
    LLM_MODEL: str = "deepseek-r1:8b"  # LLM模型名称
    LLM_DEVICE: str = "cpu"  # 强制使用 CPU
    NUM_GPU: int = 0  # 不使用 GPU
    
    # 模型参数配置
    TEMPERATURE: float = 0.3  # 温度参数，控制输出随机性
    TOP_P: float = 0.85  # 控制输出多样性
    TOP_K: int = 3  # 检索相似文档数量
    NUM_CTX: int = 4096  # 上下文窗口大小
    MAX_NEW_TOKENS: int = 512  # 最大新生成token数
    MIN_NEW_TOKENS: int = 10   # 最小新生成token数
    REPEAT_PENALTY: float = 1.1  # 重复惩罚系数
    
    # 性能优化配置
    SCORE_THRESHOLD: float = 0.5  # 相似度阈值
    FETCH_K: int = 20  # 初筛文档数量
    USE_GPU: bool = False  # 强制不使用 GPU
    USE_MEMORY_CACHE: bool = True  # 是否使用内存缓存
    CHUNK_SIZE: int = 500  # 文档分块大小
    CHUNK_OVERLAP: int = 50  # 分块重叠大小
    
    # 并发和限流配置
    MAX_CONCURRENT_REQUESTS: int = 10  # 最大并发请求数
    REQUEST_TIMEOUT: int = 30  # 请求超时时间(秒)
    RATE_LIMIT: int = 100  # 每分钟最大请求次数

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8"
    )

server_settings = ServerSettings() 