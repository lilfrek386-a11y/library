import logging
from typing import Sequence

from fastapi_cache import FastAPICache
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.models.author import AuthorModel
from .schemas import AuthorCreate, AuthorUpdatePartial, AuthorUpdate

logger = logging.getLogger(__name__)


class AuthorsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_author(self, author_id: int) -> AuthorModel | None:
        author = await self.db.get(AuthorModel, author_id)
        if author:
            logger.info("Successfully retrieved author: %s", author_id)
            return author
        else:
            logger.info("Author not found: %s", author_id)
            return None

    async def get_authors(self) -> Sequence[AuthorModel] | None:
        logger.info("Getting all authors")

        stmt = select(AuthorModel).order_by(AuthorModel.id)
        result = await self.db.execute(stmt)
        authors = result.scalars().all()

        return authors

    async def create_author(self, new_author: AuthorCreate) -> AuthorModel:
        logger.info("Creating author with data: %s", new_author)

        author = AuthorModel(**new_author.model_dump())

        self.db.add(author)
        await self.db.commit()
        await self.db.refresh(author)

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )
        logger.info("Successfully created author: %s", author.id)
        return author

    async def update_author(
        self,
        author_id: int,
        author_update: AuthorUpdate | AuthorUpdatePartial,
        partial: bool = False,
    ) -> AuthorModel | None:
        logger.info("Updating author %s with data: %s", author_id, author_update)

        author = await self.get_author(author_id)

        if not author:
            return None

        for name, value in author_update.model_dump(exclude_unset=partial).items():
            setattr(author, name, value)

        await self.db.commit()
        await self.db.refresh(author)

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.authors.author}:{author_id}"
        )

        logger.info("Successfully updated author: %s", author.id)

        return author

    async def delete_author(self, author_id: int) -> bool:
        logger.info("Deleting author: %s", author_id)

        author = await self.get_author(author_id)

        if not author:
            return False

        await self.db.delete(author)
        await self.db.commit()

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.authors.author}:{author_id}"
        )

        logger.info(f"Author deleted successfully: {author_id}")
        return True

    async def delete_all_authors(self) -> bool:
        logger.info("Deleting all authors")

        command = text("TRUNCATE TABLE authormodels RESTART IDENTITY CASCADE")

        await self.db.execute(command)
        await self.db.commit()

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )

        logger.info("All authors deleted successfully")
        return True
