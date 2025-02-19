from app.models.knowledge import KnowledgeBase, KnowledgeCreate
from typing import List, Optional

class KnowledgeService:
    def __init__(self):
        self.knowledge_items: List[KnowledgeBase] = []
        
    async def create_knowledge(self, knowledge: KnowledgeCreate) -> KnowledgeBase:
        new_knowledge = KnowledgeBase(
            id=len(self.knowledge_items) + 1,
            **knowledge.dict()
        )
        self.knowledge_items.append(new_knowledge)
        return new_knowledge
    
    async def get_knowledge(self, knowledge_id: int) -> Optional[KnowledgeBase]:
        for item in self.knowledge_items:
            if item.id == knowledge_id:
                return item
        return None 