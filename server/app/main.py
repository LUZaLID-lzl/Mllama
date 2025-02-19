from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import knowledge, data, status
from app.core.server_config import server_settings
from app.core.model_manager import model_manager

app = FastAPI(
    title=server_settings.PROJECT_NAME,
    description=server_settings.DESCRIPTION,
    version=server_settings.VERSION
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=server_settings.ALLOW_ORIGINS,
    allow_credentials=server_settings.ALLOW_CREDENTIALS,
    allow_methods=server_settings.ALLOW_METHODS,
    allow_headers=server_settings.ALLOW_HEADERS,
)

@app.on_event("startup")
async def startup_event():
    """服务启动时加载模型"""
    success = await model_manager.initialize()
    if not success:
        raise Exception("模型加载失败，服务无法启动")

# 注册路由
app.include_router(
    knowledge,
    prefix=f"{server_settings.API_V1_STR}/knowledge",
    tags=["knowledge"]
)

app.include_router(
    data,
    prefix=f"{server_settings.API_V1_STR}/data",
    tags=["data"]
)

app.include_router(
    status,
    prefix=f"{server_settings.API_V1_STR}/status",
    tags=["status"]
)

@app.get("/")
async def root():
    return {"message": "欢迎使用知识库系统"} 