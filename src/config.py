from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_USER_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_URL: str
    AUTHJWT_SECRET_KEY: str

    class Config:
        env_file = "./.env"


settings = Settings()
