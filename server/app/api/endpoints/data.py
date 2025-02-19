from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.data_service import DataService
from app.core.server_config import server_settings
from pydantic import BaseModel

router = APIRouter()
data_service = DataService()

class ProcessResponse(BaseModel):
    success: bool
    message: str
    details: Dict[str, Any] = {}

@router.post("/process", response_model=ProcessResponse)
async def process_data():
    """处理数据并构建向量数据库"""
    try:
        result = await data_service.process_and_save(server_settings.DATA_DIR)
        
        if result["success"]:
            return ProcessResponse(
                success=True,
                message="数据处理成功",
                details={
                    "total_files": result["total_files"],
                    "processed_files": result["processed_files"],
                    "skipped_files": result["skipped_files"],
                    "total_documents": result["total_documents"],
                    "total_chunks": result["total_chunks"],
                    "vector_db_path": server_settings.VECTOR_DB_PATH,
                    "processing_time": f"{result['processing_time']:.2f}秒",
                    "file_details": result["file_details"]
                }
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": "数据处理失败",
                    "error": result["error"],
                    "details": result.get("details", {})
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "数据处理过程发生错误",
                "error": str(e)
            }
        ) 