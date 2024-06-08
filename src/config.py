# Храним все данные о подключениях к различным базам, почтам и т.д.


from pydantic_settings import BaseSettings



class Settings(BaseSettings):


    DB_HOST: str # = 'localhost'
    DB_PORT: int # = 5566
    DB_USER: str # = 'soaqa'
    DB_PASS: str # = 'example'
    DB_NAME: str # = 'test_db'

    SECRET_KEY: str # JWT # bash: openssl rand -base64 32
    ALGORITHM: str  # JWT


    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    SERVICE_NAME: str
    MESSAGE_BUCKET: str


    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def MONGO_URL(self):

        return f'mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/?directConnection=true'



    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()