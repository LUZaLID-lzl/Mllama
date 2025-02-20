from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.server_config import server_settings
from app.core.model_manager import model_manager
from app.models.knowledge import StreamResponse
import asyncio
from typing import AsyncGenerator
import time
import traceback
import aiohttp
import json

class LLMService:
    def __init__(self):
        self.log_separator = "="*50
        self.max_retries = 3
        self.base_url = "http://localhost:11434"  # Ollama 默认地址
        
    def log(self, message: str, level: str = "INFO", stream: bool = False):
        """格式化日志输出"""
        timestamp = time.strftime('%H:%M:%S')
        mode = "[流式]" if stream else "[普通]"
        prefix = {
            "INFO": "📝",
            "WARN": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "THINKING": "🤔",
            "SEARCH": "🔍",
            "LLM": "🤖",
            "OUTPUT": "📤"
        }.get(level, "")
        print(f"[{timestamp}] {mode} {prefix} {message}")

    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """直接调用 Ollama API 进行流式生成"""
        timeout = aiohttp.ClientTimeout(
            total=None,
            connect=30,
            sock_read=300
        )
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "model": server_settings.LLM_MODEL,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": server_settings.TEMPERATURE,
                "top_p": server_settings.TOP_P,
                "num_ctx": server_settings.NUM_CTX,
                "repeat_penalty": server_settings.REPEAT_PENALTY
            }
        }
        
        retries = 0
        while retries < self.max_retries:
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.base_url}/api/generate",
                        headers=headers,
                        json=data
                    ) as response:
                        async for line in response.content:
                            if not line:
                                continue
                            try:
                                chunk = json.loads(line)
                                if chunk.get("done"):
                                    break
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
                return
                
            except asyncio.TimeoutError:
                retries += 1
                if retries < self.max_retries:
                    self.log(f"生成超时，正在重试 ({retries}/{self.max_retries})...", "WARN", stream=True)
                    await asyncio.sleep(1)
                else:
                    raise Exception("生成多次超时，请稍后重试")
            except Exception as e:
                raise Exception(f"生成失败: {str(e)}")

    async def query_stream(self, question: str) -> AsyncGenerator[StreamResponse, None]:
        """流式查询知识库"""
        start_time = time.time()
        
        try:
            # 1. 检查模型状态
            if not model_manager.qa_chain:
                self.log("模型未初始化，尝试初始化...", "WARN", stream=True)
                if not await model_manager.initialize():
                    raise Exception("模型初始化失败")

            # 2. 开始检索
            self.log("开始文档检索...", "SEARCH", stream=True)
            retrieval_start = time.time()
            
            try:
                docs = model_manager.vector_db.similarity_search(
                    question,
                    k=server_settings.TOP_K
                )
                
                if not docs:
                    yield StreamResponse(
                        type="error",
                        content="抱歉，未找到相关文档"
                    )
                    return
                    
            except Exception as e:
                self.log(f"文档检索失败: {str(e)}", "ERROR", stream=True)
                raise

            retrieval_time = time.time() - retrieval_start
            self.log(f"文档检索完成 (用时 {retrieval_time:.2f}秒)", "SUCCESS", stream=True)

            # 3. 发送源文档
            for i, doc in enumerate(docs):
                if model_manager.should_stop:
                    yield StreamResponse(type="stopped", content="思考已停止")
                    return
                
                yield StreamResponse(
                    type="source",
                    content=doc.page_content,
                    index=i
                )

            # 4. 流式生成回答
            self.log("开始生成回答...", "LLM", stream=True)
            
            # 构建提示词
            context = "\n".join(doc.page_content for doc in docs)
            prompt = f"""基于以下参考资料回答问题。如果无法从资料中找到答案，请说明无法回答。

参考资料：
{context}

问题：{question}

请分析后给出答案："""

            # 使用直接流式生成
            try:
                buffer = ""
                async for chunk in self.generate_stream(prompt):
                    if model_manager.should_stop:
                        yield StreamResponse(type="stopped", content="思考已停止")
                        return
                    
                    buffer += chunk
                    if len(buffer) >= 10 or chunk.endswith(("。", "!", "?", "！", "？", "\n")):
                        yield StreamResponse(
                            type="content",
                            content=buffer
                        )
                        buffer = ""
                
                # 发送剩余内容
                if buffer:
                    yield StreamResponse(
                        type="content",
                        content=buffer
                    )
                    
            except Exception as e:
                self.log(f"生成失败: {str(e)}", "ERROR", stream=True)
                raise
                
            # 5. 发送完成信号
            total_time = time.time() - start_time
            yield StreamResponse(
                type="done",
                content=f"回答完成 (总用时 {total_time:.2f}秒)"
            )
            
        except Exception as e:
            error_msg = f"查询失败: {str(e)}\n{traceback.format_exc()}"
            self.log(error_msg, "ERROR", stream=True)
            yield StreamResponse(type="error", content=error_msg)
            
        finally:
            model_manager.reset_stop_flag() 