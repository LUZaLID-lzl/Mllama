from app.api.endpoints.knowledge import router as knowledge_router
from app.api.endpoints.data import router as data_router
from app.api.endpoints.status import router as status_router

knowledge = knowledge_router
data = data_router
status = status_router 