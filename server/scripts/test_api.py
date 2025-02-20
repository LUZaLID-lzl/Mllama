# -*- coding: utf-8 -*-
import requests
import json

def test_default_questions():
    """测试获取默认问题列表"""
    url = "http://localhost:8000/api/v1/knowledge/default-questions"
    
    try:
        print("\n" + "="*50)
        print("测试获取默认问题列表")
        print("="*50)
        
        response = requests.get(url)
        response.raise_for_status()  # 检查响应状态
        
        questions = response.json()
        print("\n获取到 {} 个问题:".format(len(questions)))
        
        for i, q in enumerate(questions, 1):
            print("\n问题 {}:".format(i))
            print("类别: {}".format(q['category']))
            print("标题: {}".format(q['title']))
            print("问题: {}".format(q['question']))
        
        print("\n" + "="*50)
        
    except Exception as e:
        print("请求失败: {}".format(str(e)))
        if hasattr(e, 'response'):
            print("响应状态码: {}".format(e.response.status_code))
            print("响应内容: {}".format(e.response.text))

def test_query(question):
    """测试问答接口"""
    url = "http://localhost:8000/api/v1/knowledge/query"
    headers = {"Content-Type": "application/json"}
    data = {"question": question}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("\n问题:", question)
        print("\n回答:", result["answer"])
        print("\n参考来源:")
        for source in result["sources"]:
            print("-", source["content"])
        print("\n" + "="*50)
        
    except Exception as e:
        print("请求失败: {}".format(str(e)))

if __name__ == "__main__":
    # 测试获取默认问题
    test_default_questions()
    
    # 测试问答功能
    questions = [
        "如何提高ODEX优化进度",
    ]
    
    for q in questions:
        test_query(q) 