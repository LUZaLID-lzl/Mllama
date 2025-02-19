# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

import uvicorn
from app.core.server_config import server_settings

def run_server():
    """启动服务器"""
    uvicorn.run(
        "app.main:app",
        host=server_settings.HOST,
        port=server_settings.PORT,
        reload=server_settings.RELOAD,
        workers=server_settings.WORKERS
    )

if __name__ == "__main__":
    run_server() 