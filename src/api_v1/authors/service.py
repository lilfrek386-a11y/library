import logging
from fastapi_cache import FastAPICache

from src.core.mixins import ServiceMixin
from src.core.config import settings
from src.api_v1.authors.repository import AuthorsRepository
from src.api_v1.authors.schemas import *

logger = logging.getLogger(__name__)


class AuthorsService(ServiceMixin):
    def __init__(self, author_repo: AuthorsRepository):
        self.author_repo = author_repo

    async def get_authors(self) -> list[AuthorId]:
        logger.info("Get all authors")
        authors = await self.author_repo.get_all()
        return [AuthorId.model_validate(x) for x in authors]

    async def get_author(self, author_id: int) -> AuthorId:
        logger.info(f"Get author {author_id}")

        author = self.get_or_404(
            await self.author_repo.get_one(author_id), detail="Author not found"
        )

        return AuthorId.model_validate(author)

    async def create_author(self, new_author: AuthorCreate) -> AuthorId:
        logger.info(f"Creating author: {new_author.first_name}")

        author = await self.author_repo.create(new_author.model_dump())

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )
        return AuthorId.model_validate(author)

    async def update_author(
        self,
        author_id: int,
        author_update: AuthorUpdate | AuthorUpdatePartial,
        partial: bool = False,
    ) -> AuthorId:

        author = self.get_or_404(
            await self.author_repo.get_one(author_id), detail="Author not found"
        )

        update_data = author_update.model_dump(exclude_unset=partial)

        updated_author = await self.author_repo.update(
            db_obj=author, update_data=update_data
        )

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.authors.author}:{author_id}"
        )

        return AuthorId.model_validate(updated_author)

    async def delete_author(self, author_id: int) -> None:
        logger.info(f"Deleting author {author_id}")

        author = self.get_or_404(
            await self.author_repo.get_one(author_id), detail="Author not found"
        )

        await self.author_repo.delete(author)

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.authors.author}:{author_id}"
        )

    async def delete_all_authors(self):
        logger.info(f"Delete all authors")

        await self.author_repo.delete_all_authors()

        await FastAPICache.clear(
            namespace=settings.cache.namespace.authors.authors_list
        )
