# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.services.data_service import DataService
from app.core.server_config import server_settings

def process_data():
    """处理文档并创建向量库"""
    try:
        print("\n=== 开始处理文档 ===")
        
        # 检查数据目录
        data_dir = server_settings.DATA_DIR
        if not os.path.exists(data_dir):
            print(f"错误: 数据目录不存在: {data_dir}")
            return False
            
        # 创建数据服务
        data_service = DataService()
        
        # 处理文档
        result = data_service.process_documents()
        
        if result["success"]:
            print("\n处理成功:")
            print(f"- 总文件数: {result['total_files']}")
            print(f"- 处理文件数: {result['processed_files']}")
            print(f"- 跳过文件数: {result['skipped_files']}")
            print(f"- 总文档数: {result['total_documents']}")
            print(f"- 总块数: {result['total_chunks']}")
            print(f"- 处理时间: {result['processing_time']:.2f}秒")
            return True
        else:
            print("\n处理失败:")
            print(f"错误: {result['error']}")
            print("详细信息:", result['details'])
            return False
            
    except Exception as e:
        print(f"处理文档时出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = process_data()
    sys.exit(0 if success else 1) 