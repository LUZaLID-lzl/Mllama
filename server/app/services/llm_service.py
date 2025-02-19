from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.llm_config import llm_settings
import os
from app.core.model_manager import model_manager
from app.models.knowledge import SourceDocument, StreamResponse
import asyncio
from typing import AsyncGenerator

class LLMService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=llm_settings.EMBEDDING_MODEL
        )
        self.llm = Ollama(
            model=llm_settings.LLM_MODEL,
            temperature=llm_settings.TEMPERATURE,
            num_ctx=llm_settings.NUM_CTX,
            num_gpu=llm_settings.NUM_GPU
        )
        self.vector_db = None
        self.qa_chain = None
        
    def _load_vector_db(self):
        """加载向量数据库"""
        if not os.path.exists(llm_settings.VECTOR_DB_PATH):
            raise Exception("向量数据库不存在，请先处理数据")
        
        self.vector_db = FAISS.load_local(
            llm_settings.VECTOR_DB_PATH,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vector_db.as_retriever(
                search_kwargs={"k": llm_settings.TOP_K}
            ),
            chain_type="stuff",
            return_source_documents=True
        )
    
    async def query(self, question: str) -> dict:
        """查询知识库"""
        try:
            result = model_manager.qa_chain({"query": question})
            
            # 处理来源文档
            sources = []
            for doc in result["source_documents"]:
                sources.append(SourceDocument(
                    content=doc.page_content,
                    # 如果有相关度分数，可以添加
                    # relevance=doc.metadata.get('relevance')
                ))
            
            return {
                "answer": result["result"],
                "sources": sources
            }
        except Exception as e:
            raise Exception(f"查询失败: {str(e)}")

    async def query_stream(self, question: str) -> AsyncGenerator[StreamResponse, None]:
        """流式查询知识库"""
        try:
            # 重置停止标志
            model_manager.reset_stop_flag()
            
            # 1. 发送思考中的消息
            yield StreamResponse(
                type="thinking",
                content="正在思考中..."
            )
            
            # 检查是否应该停止
            if model_manager.should_stop:
                yield StreamResponse(
                    type="stopped",
                    content="思考已停止"
                )
                return
            
            # 2. 获取相关文档
            search_kwargs = {"k": model_manager.server_settings.TOP_K}
            docs = model_manager.vector_db.similarity_search(question, **search_kwargs)
            
            # 3. 发送找到的相关文档
            for i, doc in enumerate(docs):
                if model_manager.should_stop:
                    yield StreamResponse(
                        type="stopped",
                        content="思考已停止"
                    )
                    return
                    
                yield StreamResponse(
                    type="source",
                    content=doc.page_content,
                    index=i
                )
            
            # 4. 生成答案
            result = model_manager.qa_chain({"query": question})
            
            # 5. 分段发送答案
            sentences = result["result"].split("。")
            for sentence in sentences:
                if model_manager.should_stop:
                    yield StreamResponse(
                        type="stopped",
                        content="思考已停止"
                    )
                    return
                    
                if sentence.strip():
                    yield StreamResponse(
                        type="content",
                        content=sentence + "。"
                    )
                    await asyncio.sleep(0.5)
            
            # 6. 发送完成信号
            yield StreamResponse(
                type="done",
                content="回答完成"
            )
            
        except Exception as e:
            yield StreamResponse(
                type="error",
                content=f"查询失败: {str(e)}"
            )
        finally:
            # 重置停止标志
            model_manager.reset_stop_flag() 