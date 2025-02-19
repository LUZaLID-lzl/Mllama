import os
import time
from typing import Dict, Any, List, Tuple
from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    JSONLoader,
    UnstructuredMarkdownLoader
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.server_config import server_settings

class DataService:
    def __init__(self):
        self.LOADER_CONFIG = {
            ".txt": {
                "loader": TextLoader,
                "args": {"encoding": "utf-8"}
            },
            ".csv": {
                "loader": CSVLoader,
                "args": {"csv_args": {"fieldnames": ["question", "answer"]}}
            },
            ".json": {
                "loader": JSONLoader,
                "args": {"jq_schema": ".[] | {question: .q, answer: .a}"}
            },
            ".md": {
                "loader": UnstructuredMarkdownLoader,
                "args": {}
            }
        }
        
        self.reset_stats()

    def reset_stats(self):
        """重置处理统计"""
        self.processing_stats = {
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "total_documents": 0,
            "total_chunks": 0,
            "file_details": []
        }

    async def load_all_documents(self, data_dir: str) -> Tuple[List, Dict[str, Any]]:
        """加载目录下所有支持格式的文件"""
        self.reset_stats()
        documents = []
        
        if not os.path.exists(data_dir):
            raise Exception(f"数据目录不存在: {data_dir}")
        
        for root, _, files in os.walk(data_dir):
            self.processing_stats["total_files"] += len(files)
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                file_stat = {
                    "file_name": file,
                    "file_path": file_path,
                    "file_type": file_ext,
                    "status": "skipped",
                    "documents": 0,
                    "error": None
                }
                
                if file_ext not in self.LOADER_CONFIG:
                    self.processing_stats["skipped_files"] += 1
                    file_stat["status"] = "skipped"
                    file_stat["error"] = "不支持的文件格式"
                    self.processing_stats["file_details"].append(file_stat)
                    print(f"跳过不支持的文件: {file_path}")
                    continue
                    
                try:
                    config = self.LOADER_CONFIG[file_ext]
                    loader = config["loader"](file_path, **config["args"])
                    file_docs = loader.load()
                    documents.extend(file_docs)
                    
                    self.processing_stats["processed_files"] += 1
                    file_stat["status"] = "success"
                    file_stat["documents"] = len(file_docs)
                    print(f"成功处理文件: {file_path}")
                    
                except Exception as e:
                    self.processing_stats["skipped_files"] += 1
                    file_stat["status"] = "error"
                    file_stat["error"] = str(e)
                    print(f"处理文件失败 {file_path}: {str(e)}")
                
                self.processing_stats["file_details"].append(file_stat)
                
        self.processing_stats["total_documents"] = len(documents)
        return documents, self.processing_stats

    async def process_and_save(self, data_dir: str) -> Dict[str, Any]:
        """处理数据并保存向量数据库"""
        start_time = time.time()
        
        try:
            # 1. 加载数据
            print(f"开始处理目录: {data_dir}")
            all_documents, stats = await self.load_all_documents(data_dir)
            
            if not all_documents:
                return {
                    "success": False,
                    "error": "没有找到可处理的文档",
                    "details": stats
                }

            # 2. 分块处理
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=50,
                separators=["\n问题:", "\n---\n", "\n"]
            )
            texts = text_splitter.split_documents(all_documents)
            stats["total_chunks"] = len(texts)
            print(f"文档分块完成，共 {len(texts)} 个文本块")

            # 3. 构建向量数据库
            print("开始构建向量数据库...")
            embeddings = HuggingFaceEmbeddings(
                model_name=server_settings.EMBEDDING_MODEL
            )
            vector_db = FAISS.from_documents(texts, embeddings)
            
            # 确保保存目录存在
            os.makedirs(server_settings.VECTOR_DB_PATH, exist_ok=True)
            vector_db.save_local(server_settings.VECTOR_DB_PATH)
            print(f"向量数据库已保存到: {server_settings.VECTOR_DB_PATH}")
            
            # 4. 计算处理时间
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "total_files": stats["total_files"],
                "processed_files": stats["processed_files"],
                "skipped_files": stats["skipped_files"],
                "total_documents": stats["total_documents"],
                "total_chunks": stats["total_chunks"],
                "processing_time": processing_time,
                "file_details": stats["file_details"]
            }
            
        except Exception as e:
            print(f"处理失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "details": self.processing_stats
            } 