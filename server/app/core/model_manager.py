from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.server_config import server_settings

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
            self._initialized = True
            self._should_stop = False  # 添加停止标志

    async def initialize(self):
        """初始化模型和向量数据库"""
        try:
            print("开始加载模型...")
            
            # 1. 加载向量数据库
            self.embeddings = HuggingFaceEmbeddings(
                model_name=server_settings.EMBEDDING_MODEL
            )
            self.vector_db = FAISS.load_local(
                server_settings.VECTOR_DB_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("向量数据库加载完成")

            # 2. 加载本地模型
            self.llm = Ollama(
                model=server_settings.LLM_MODEL,
                temperature=server_settings.TEMPERATURE,
                num_ctx=server_settings.NUM_CTX,
                num_gpu=server_settings.NUM_GPU
            )
            print("本地模型加载完成")

            # 3. 创建检索链
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                retriever=self.vector_db.as_retriever(
                    search_kwargs={"k": server_settings.TOP_K}
                ),
                chain_type="stuff",
                return_source_documents=True
            )
            print("检索链创建完成")
            
            return True
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
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