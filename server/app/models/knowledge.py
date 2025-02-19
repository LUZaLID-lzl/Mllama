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