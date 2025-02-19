# -*- coding: utf-8 -*-
import requests
import json

def test_query(question: str):
    url = "http://localhost:8000/api/v1/knowledge/query"
    headers = {"Content-Type": "application/json"}
    data = {"question": question}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # 检查响应状态
        
        result = response.json()
        print("\n问题:", question)
        print("\n回答:", result["answer"])
        print("\n参考来源:")
        for source in result["sources"]:
            print("-", source["content"])
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    # 测试一些问题
    questions = [
        "如何提高ODEX优化进度",
    ]
    
    for q in questions:
        test_query(q) 