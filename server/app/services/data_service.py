import os
import time
from pathlib import Path
from typing import List, Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.server_config import server_settings
from app.utils.document_processor import DocumentProcessor

class DataService:
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.md', '.markdown'}
        
    def process_documents(self) -> Dict:
        """处理文档并构建向量数据库"""
        start_time = time.time()
        result = {
            "success": False,
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "total_documents": 0,
            "total_chunks": 0,
            "processing_time": 0,
            "error": None,
            "details": []
        }
        
        try:
            print("\n=== 开始处理文档 ===")
            
            # 1. 检查数据目录
            data_dir = server_settings.DATA_DIR
            if not os.path.exists(data_dir):
                raise Exception(f"数据目录不存在: {data_dir}")
            
            # 2. 处理所有文档
            all_documents = []
            
            for root, _, files in os.walk(data_dir):
                result["total_files"] += len(files)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext not in self.supported_extensions:
                        print(f"跳过不支持的文件: {file}")
                        result["skipped_files"] += 1
                        continue
                    
                    try:
                        print(f"\n处理文件: {file}")
                        documents = self.doc_processor.process_file(file_path)
                        
                        if documents:
                            all_documents.extend(documents)
                            result["processed_files"] += 1
                            result["total_chunks"] += len(documents)
                            print(f"✓ 成功处理 {len(documents)} 个文档块")
                        else:
                            print("✗ 文件内容为空")
                            result["skipped_files"] += 1
                            
                    except Exception as e:
                        print(f"✗ 处理失败: {str(e)}")
                        result["skipped_files"] += 1
                        result["details"].append({
                            "file": file,
                            "error": str(e)
                        })
            
            if not all_documents:
                raise Exception("没有找到可处理的文档")
            
            result["total_documents"] = len(all_documents)
            print(f"\n共处理 {result['total_documents']} 个文档块")
            
            # 3. 构建向量数据库
            print("\n=== 构建向量数据库 ===")
            
            # 设置设备
            device = "cuda" if server_settings.USE_GPU else "cpu"
            print(f"使用设备: {device}")
            
            # 初始化 Embedding 模型
            embeddings = HuggingFaceEmbeddings(
                model_name=server_settings.EMBEDDING_MODEL,
                model_kwargs={'device': device},
                encode_kwargs={
                    'batch_size': server_settings.EMBEDDING_BATCH_SIZE,
                    'device': device,
                    'normalize_embeddings': True
                }
            )
            
            # 创建向量数据库
            vector_db = FAISS.from_documents(all_documents, embeddings)
            
            # 保存向量数据库
            vector_db_path = server_settings.VECTOR_DB_PATH
            os.makedirs(vector_db_path, exist_ok=True)
            vector_db.save_local(vector_db_path)
            
            print(f"向量数据库已保存到: {vector_db_path}")
            
            result["success"] = True
            result["processing_time"] = time.time() - start_time
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            return result 