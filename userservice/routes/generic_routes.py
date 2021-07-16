from fastapi import APIRouter
from models import ServerHealth


generic_router = APIRouter()


@generic_router.get('/', response_model=ServerHealth)
async def health():
    return ServerHealth(name='user-service')
