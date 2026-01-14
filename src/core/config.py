from pathlib import Path

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = (Path(__file__)).parent.parent


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


class AuthorsNamespace(BaseModel):
    authors_list: str = "authors_list"
    author: str = "author"


class BooksNamespace(BaseModel):
    books_list: str = "books_list"
    book: str = "book"


class CacheNamespace(BaseModel):
    authors: AuthorsNamespace = AuthorsNamespace()
    books: BooksNamespace = BooksNamespace()


class CacheConfig(BaseModel):
    prefix: str = "cache"
    namespace: CacheNamespace = CacheNamespace()


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"


class Settings(BaseSettings):
    db: DBConfig = DBConfig()
    redis: RedisConfig = RedisConfig()
    cache: CacheConfig = CacheConfig()
    auth_jwt: AuthJWT = AuthJWT()
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
