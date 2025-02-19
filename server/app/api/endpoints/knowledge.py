from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.knowledge import (
    KnowledgeCreate, 
    KnowledgeBase, 
    Query, 
    QueryResponse,
    QueryRequest,
    StreamResponse
)
from app.services.knowledge_service import KnowledgeService
from app.services.llm_service import LLMService
import json
from app.core.model_manager import ModelManager
from langchain_huggingface import HuggingFaceEmbeddings

router = APIRouter()
knowledge_service = KnowledgeService()
llm_service = LLMService()
model_manager = ModelManager()

@router.post("/", response_model=KnowledgeBase)
async def create_knowledge(knowledge: KnowledgeCreate):
    return await knowledge_service.create_knowledge(knowledge)

@router.get("/{knowledge_id}", response_model=KnowledgeBase)
async def get_knowledge(knowledge_id: int):
    knowledge = await knowledge_service.get_knowledge(knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="知识条目未找到")
    return knowledge

@router.post("/query")
async def query_knowledge(query: QueryRequest):
    """
    知识库问答接口
    支持普通响应和流式响应
    """
    if not query.stream:
        # 普通响应
        try:
            result = await llm_service.query(query.question)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # 流式响应
    async def generate():
        async for response in llm_service.query_stream(query.question):
            yield f"data: {json.dumps(response.dict(), ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@router.post("/stop")
async def stop_thinking():
    """停止当前的思考过程"""
    try:
        model_manager.stop_thinking()
        return {"message": "已发送停止信号"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 