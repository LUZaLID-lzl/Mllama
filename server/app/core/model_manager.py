from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.server_config import server_settings
import torch
import os

class ModelManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.embeddings = None
            self.vector_db = None
            self.llm = None
            self.qa_chain = None
            self._should_stop = False
            self.server_settings = server_settings
            self._initialized = True

    async def initialize(self):
        """初始化模型和向量数据库"""
        try:
            print("\n=== 开始初始化模型 ===")
            
            # 1. 设置设备
            device = (
                self.server_settings.EMBEDDING_DEVICE 
                if torch.cuda.is_available() and self.server_settings.USE_GPU 
                else "cpu"
            )
            print(f"使用设备: {device}")
            
            # 2. 初始化 Embedding 模型
            print(f"加载 Embedding 模型: {self.server_settings.EMBEDDING_MODEL}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.server_settings.EMBEDDING_MODEL,
                model_kwargs={'device': device},
                encode_kwargs={
                    'batch_size': self.server_settings.EMBEDDING_BATCH_SIZE,
                    'device': device,
                    'normalize_embeddings': True
                }
            )
            
            # 3. 检查向量库
            vector_db_path = self.server_settings.VECTOR_DB_PATH
            print(f"检查向量库路径: {vector_db_path}")
            
            if not os.path.exists(vector_db_path):
                print("警告: 向量库不存在，需要先处理文档")
                return False
                
            try:
                print("加载向量库...")
                self.vector_db = FAISS.load_local(
                    vector_db_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"向量库加载成功")
            except Exception as e:
                print(f"向量库加载失败，可能需要重新处理文档: {str(e)}")
                return False
            
            # 4. 初始化 LLM
            print(f"初始化 LLM 模型: {self.server_settings.LLM_MODEL}")
            self.llm = Ollama(
                model=self.server_settings.LLM_MODEL,
                temperature=self.server_settings.TEMPERATURE,
                top_p=self.server_settings.TOP_P,
                num_ctx=self.server_settings.NUM_CTX,
                repeat_penalty=self.server_settings.REPEAT_PENALTY,
                num_gpu=self.server_settings.NUM_GPU if device == "cuda" else 0,
                timeout=self.server_settings.REQUEST_TIMEOUT
            )
            
            # 5. 创建问答链
            print("创建问答链...")
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_db.as_retriever(
                    search_kwargs={
                        "k": self.server_settings.TOP_K,
                        "score_threshold": self.server_settings.SCORE_THRESHOLD,
                        "fetch_k": self.server_settings.FETCH_K
                    }
                )
            )
            
            print("=== 模型初始化完成 ===\n")
            return True
            
        except Exception as e:
            print(f"模型初始化失败: {str(e)}")
            return False

    def stop_thinking(self):
        """停止当前的思考过程"""
        self._should_stop = True
    
    def reset_stop_flag(self):
        """重置停止标志"""
        self._should_stop = False
    
    @property
    def should_stop(self):
        """获取停止标志状态"""
        return self._should_stop

model_manager = ModelManager() 