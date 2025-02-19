from fastapi import APIRouter
from typing import Dict, Any
from app.core.model_manager import model_manager
from app.core.server_config import server_settings

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_status():
    """
    获取服务状态
    
    返回：
    - server_info: 服务器信息
    - model_info: 模型信息
    - vector_db_info: 向量数据库信息
    """
    try:
        status = {
            "server_info": {
                "name": server_settings.PROJECT_NAME,
                "version": server_settings.VERSION,
                "status": "running"
            },
            "model_info": {
                "embedding_model": server_settings.EMBEDDING_MODEL,
                "llm_model": server_settings.LLM_MODEL,
                "model_loaded": model_manager.llm is not None
            },
            "vector_db_info": {
                "path": server_settings.VECTOR_DB_PATH,
                "db_loaded": model_manager.vector_db is not None,
                "top_k": server_settings.TOP_K
            }
        }
        return status
    except Exception as e:
        return {
            "server_info": {
                "name": server_settings.PROJECT_NAME,
                "version": server_settings.VERSION,
                "status": "error",
                "error": str(e)
            }
        } 