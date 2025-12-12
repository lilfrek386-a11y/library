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


class RedisConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: int = 0

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="REDIS_", extra="ignore"
    )

class AuthorsNamespace(BaseSettings):
    authors_list: str = "authors_list"
    author: str = "author"

class BooksNamespace(BaseSettings):
    books_list: str = "books_list"
    book: str = "book"

class CacheNamespace(BaseSettings):
    authors: AuthorsNamespace = AuthorsNamespace()
    books: BooksNamespace = BooksNamespace()


class CacheConfig(BaseSettings):
    prefix: str = "cache"
    namespace: CacheNamespace = CacheNamespace()


class Settings(BaseSettings):
    db: DBConfig = DBConfig()
    redis: RedisConfig = RedisConfig()
    cache: CacheConfig = CacheConfig()
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
