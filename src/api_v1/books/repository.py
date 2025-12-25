import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base_repository import BaseRepository
from src.core.models.book import BookModel


logger = logging.getLogger(__name__)


class BooksRepository(BaseRepository[BookModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(model=BookModel, db=db)

    async def delete_all_books(self) -> None:
        command = text("TRUNCATE TABLE books RESTART IDENTITY CASCADE")

        await self.db.execute(command)
        await self.db.commit()
