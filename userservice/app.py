import motor
from beanie import init_beanie
from fastapi import FastAPI
from pydantic import BaseSettings

from .models import UserDB
from .routes.user_routes import users_router
from .routes.generic_routes import generic_router
import logging

LOGGER = logging.getLogger(__name__)

app = FastAPI()

class Settings(BaseSettings):
    mongo_dsn: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@app.on_event("startup")
async def app_init(settings: Settings = Settings()):
    # CREATE MOTOR CLIENT
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.mongo_dsn
    )

    # INIT BEANIE
    await init_beanie(client.beanie_db, document_models=[UserDB])


    app.include_router(users_router, prefix="/v1", tags=["users"])
    app.include_router(generic_router, tags=["server"])
    app.is_app_ready = True


