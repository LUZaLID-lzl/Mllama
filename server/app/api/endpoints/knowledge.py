from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.knowledge import (
    KnowledgeCreate, 
    KnowledgeBase, 
    Query, 
    QueryResponse,
    QueryRequest,
    StreamResponse,
    DefaultQuestion
)
from app.services.knowledge_service import KnowledgeService
from app.services.llm_service import LLMService
import json
from app.core.model_manager import ModelManager
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict
from app.services.question_service import QuestionService

router = APIRouter()
knowledge_service = KnowledgeService()
llm_service = LLMService()
model_manager = ModelManager()
question_service = QuestionService()

# 添加默认问题列表
DEFAULT_QUESTIONS = [
    {
        "id": 1,
        "title": "GMS认证",
        "question": "GMS认证流程介绍"
    },
    {
        "id": 2,
        "title": "ODEX优化",
        "question": "如何提高ODEX优化进度?"
    },
    {
        "id": 3,
        "title": "系统性能",
        "question": "Android系统性能优化的主要方法有哪些?"
    }
]

@router.get("/default-questions", response_model=List[DefaultQuestion])
async def get_default_questions():
    """获取默认问题列表（每次随机3个）"""
    try:
        questions = question_service.get_random_questions(count=3)
        print(f"获取到 {len(questions)} 个问题")
        
        if not questions:
            print("警告: 没有获取到任何问题")
            return [
                DefaultQuestion(
                    id=1,
                    title="GMS认证流程",
                    question="GMS认证流程介绍",
                    category="GMS认证"
                )
            ]
        
        # 验证数据结构
        for q in questions:
            if not all(k in q for k in ["id", "title", "question", "category"]):
                print(f"警告: 问题数据结构不完整: {q}")
                continue
        
        return [
            DefaultQuestion(
                id=q["id"],
                title=q["title"],
                question=q["question"],
                category=q["category"]
            ) for q in questions if all(k in q for k in ["id", "title", "question", "category"])
        ]
    except Exception as e:
        print(f"处理默认问题失败: {str(e)}")
        return [
            DefaultQuestion(
                id=1,
                title="GMS认证流程",
                question="GMS认证流程介绍",
                category="GMS认证"
            )
        ]

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