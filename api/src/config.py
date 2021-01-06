"""
API configs.
"""
import os
from functools import lru_cache

from loguru import logger
from pydantic import BaseSettings


ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENVIRONMENT: str = os.environ.get("ENVIRONMENT")


class Settings(BaseSettings):
    SECRET_KEY = "Cu5WWO5bd-H7cBpBJvC6VHlPk7e-lXvmh26ibEq3UJz="
    SALT = "$3b$12$n9D6hxmvZ/tV0peAW4Npbg"
    LOG_PATH = "/var/log/bicklebow"
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN")
    CERTIFICATE = f"{ROOT_PATH}/configs/cert.pem"
    SERVER_IP: str = os.environ.get("SERVER_IP")

    class Config:
        env_file = f"{ROOT_PATH}/configs/.{ENVIRONMENT}.env"

    @property
    def SQLITE_URI(self):
        return f"sqlite:///{ROOT_PATH}/api/src/bicklebow.db"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


logger.add(
    f"{settings.LOG_PATH}/out.log",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>{level: <8}</cyan> <level>{message}</level>",
    level="DEBUG",
    colorize=True,
    retention="30 days",
    rotation="6 days",
)
logger.add(
    f"{settings.LOG_PATH}/err.log",
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>{level: <8}</cyan> <level>{message}</level>",
    level="ERROR",
    colorize=True,
    retention="30 days",
    rotation="6 days",
)
