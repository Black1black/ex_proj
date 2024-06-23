# Храним все данные о подключениях к различным базам, почтам и т.д.


from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DB_HOST: str
    DB_PORT: int 
    DB_USER: str 
    DB_PASS: str 
    DB_NAME: str 

    SECRET_KEY: str 
    ALGORITHM: str  

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    MINIO_ACCESS_KEY_ID: str
    MINIO_SECRET_ACCESS_KEY: str
    MINIO_HOST: str
    MINIO_PORT: int
    MESSAGE_BUCKET: str
    PROFILE_BUCKET: str


    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def MONGO_URL(self):

        return f'mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/?directConnection=true'

    @property
    def MINIO_URL(self):
        return f'https://{self.MINIO_HOST}:{self.MINIO_PORT}'



    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()