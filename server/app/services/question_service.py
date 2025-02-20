import json
import random
from typing import List, Dict
from pathlib import Path
import os

class QuestionService:
    def __init__(self):
        # 修改路径获取方式
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent
        self.question_bank_path = project_root / "data" / "question_bank.json"
        print(f"问题库路径: {self.question_bank_path}")  # 添加调试日志
        self.question_bank = self._load_question_bank()

    def _load_question_bank(self) -> dict:
        """加载问题库"""
        try:
            if not os.path.exists(self.question_bank_path):
                print(f"问题库文件不存在: {self.question_bank_path}")  # 添加调试日志
                raise FileNotFoundError(f"问题库文件不存在: {self.question_bank_path}")
            
            with open(self.question_bank_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"成功加载问题库: {len(data.get('questions', []))} 个类别")  # 添加调试日志
                return data
        except Exception as e:
            print(f"加载问题库失败: {str(e)}")
            # 返回一些默认问题，避免完全失败
            return {
                "questions": [
                    {
                        "id": 1,
                        "category": "GMS认证",
                        "questions": [
                            {
                                "title": "GMS认证流程",
                                "question": "GMS认证流程介绍"
                            }
                        ]
                    }
                ]
            }

    def get_random_questions(self, count: int = 3) -> List[Dict]:
        """随机获取指定数量的问题"""
        try:
            all_questions = []
            for category in self.question_bank.get("questions", []):
                for q in category.get("questions", []):
                    all_questions.append({
                        "id": len(all_questions) + 1,
                        "title": q.get("title", ""),
                        "question": q.get("question", ""),
                        "category": category.get("category", "")
                    })
            
            print(f"找到 {len(all_questions)} 个问题")  # 添加调试日志
            
            if not all_questions:
                print("警告: 没有找到任何问题")
                return []
                
            # 随机选择问题
            count = min(count, len(all_questions))
            selected = random.sample(all_questions, count)
            print(f"随机选择了 {len(selected)} 个问题")  # 添加调试日志
            
            return selected
            
        except Exception as e:
            print(f"获取随机问题失败: {str(e)}")
            return [] 