from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseSettings):
    host: str
    port: int
    user: str
    password: str = Field(alias="DB_PASS")
    name: str
    echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DB_", extra="ignore")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"




class Settings(BaseSettings):
    db: DBConfig = DBConfig()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
