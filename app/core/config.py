from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DB_ENV: str = "local"  # "docker" или "local"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST_LOCAL: str
    DB_HOST_DOCKER: str
    DB_PORT: int = 5432

    @property
    def DB_HOST(self) -> str:
        return self.DB_HOST_DOCKER if self.DB_ENV == "docker" else self.DB_HOST_LOCAL

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.POSTGRES_DB}"
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
