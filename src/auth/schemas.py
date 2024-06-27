from pydantic import BaseModel, Field


class STokens(BaseModel):
    "Делаем схему для перевода в camelCase в мобильном приложении"
    access_token: str = Field(alias="accessToken")
    refresh_token: str | None = Field(alias="refreshToken")

    class Config:
        populate_by_name = True
