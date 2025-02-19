# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import List
import logging

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.server_config import server_settings
from app.utils.document_processor import DocumentProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_data(data_dir: str = None):
    """处理数据并构建向量数据库"""
    try:
        if data_dir is None:
            data_dir = os.path.join(project_root, "data")
            
        logger.info(f"开始处理目录: {data_dir}")
        
        # 初始化文档处理器
        doc_processor = DocumentProcessor()
        all_documents = []
        
        # 处理所有支持的文件
        supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.md', '.markdown'}
        
        for root, _, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext not in supported_extensions:
                    logger.warning(f"跳过不支持的文件: {file_path}")
                    continue
                    
                try:
                    logger.info(f"处理文件: {file_path}")
                    documents = doc_processor.process_file(file_path)
                    all_documents.extend(documents)
                    logger.info(f"成功处理文件: {file_path}, 生成 {len(documents)} 个文档片段")
                except Exception as e:
                    logger.error(f"处理文件失败 {file_path}: {str(e)}")
        
        if not all_documents:
            raise ValueError("没有找到可处理的文档")
            
        logger.info(f"共处理 {len(all_documents)} 个文档片段")
        
        # 构建向量数据库
        logger.info("开始构建向量数据库...")
        embeddings = HuggingFaceEmbeddings(
            model_name=server_settings.EMBEDDING_MODEL
        )
        vector_db = FAISS.from_documents(all_documents, embeddings)
        
        # 确保保存目录存在
        os.makedirs(server_settings.VECTOR_DB_PATH, exist_ok=True)
        vector_db.save_local(server_settings.VECTOR_DB_PATH)
        logger.info(f"向量数据库已保存到: {server_settings.VECTOR_DB_PATH}")
        
        return True
        
    except Exception as e:
        logger.error(f"处理数据失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 可以通过命令行参数指定数据目录
    data_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = process_data(data_dir)
    sys.exit(0 if success else 1) 