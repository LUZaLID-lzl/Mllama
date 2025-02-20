from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class KnowledgeBase(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    tags: List[str] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class KnowledgeCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class Query(BaseModel):
    question: str

class SourceDocument(BaseModel):
    content: str
    relevance: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument] = []

class StreamResponse(BaseModel):
    type: str  # 'thinking' | 'content' | 'source' | 'done' | 'stopped' | 'error'
    content: str
    index: Optional[int] = None  # 用于源文档的索引

class QueryRequest(BaseModel):
    question: str
    stream: bool = False  # 是否使用流式响应

class QuestionItem(BaseModel):
    title: str
    question: str

class QuestionCategory(BaseModel):
    id: int
    category: str
    questions: List[QuestionItem]

class QuestionBank(BaseModel):
    questions: List[QuestionCategory]

class DefaultQuestion(BaseModel):
    id: int
    title: str
    question: str
    category: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "GMS认证流程",
                "question": "GMS认证流程介绍",
                "category": "GMS认证"
            }
        }

# 可以删除这个类，因为我们直接返回 List[DefaultQuestion]
# class DefaultQuestionsResponse(BaseModel):
#     questions: List[DefaultQuestion] 