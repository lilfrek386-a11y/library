from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import AuthorModel
from src.core.base_repository import BaseRepository


class AuthorsRepository(BaseRepository[AuthorModel]):

    def __init__(self, db: AsyncSession):
        super().__init__(model=AuthorModel, db=db)

    async def delete_all_authors(self) -> None:
        command = text("TRUNCATE TABLE authors RESTART IDENTITY CASCADE")

        await self.db.execute(command)
        await self.db.commit()
