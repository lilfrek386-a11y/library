import logging
from typing import Sequence

from fastapi_cache import FastAPICache
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.models.book import BookModel
from .schemas import BookUpdate, BookCreate, BookUpdatePartial
from ..authors.author_repository import AuthorsRepository

logger = logging.getLogger(__name__)


class BookRepository:
    def __init__(self, db: AsyncSession, authors_repo: AuthorsRepository):
        self.db = db
        self.authors_repo = authors_repo

    async def get_book(self, book_id: int) -> BookModel | None:
        book = await self.db.get(BookModel, book_id)
        if book:
            logger.info("Successfully retrieved book: %s", book_id)
            return book
        else:
            logger.info("Book not found: %s", book_id)
            return None

    async def get_books(self) -> Sequence[BookModel]:
        logger.info("Getting all books")

        stmt = select(BookModel).order_by(BookModel.id)
        result = await self.db.execute(stmt)
        books = result.scalars().all()

        return books

    async def create_book(self, new_book: BookCreate) -> BookModel | None:
        logger.info("Creating book with data: %s", new_book)

        if not await self.authors_repo.get_author(new_book.author_id):
            return None

        await FastAPICache.clear(namespace=settings.cache.namespace.books.books_list)

        book = BookModel(**new_book.model_dump())

        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)

        logger.info("Successfully created book: %s", book.id)
        return book

    async def update_book(
        self,
        book_id: int,
        book_update: BookUpdate | BookUpdatePartial,
        partial: bool = False,
    ) -> BookModel | None:
        logger.info("Updating book %s with data: %s", book_id, book_update)

        if getattr(book_update, "author_id", None) is not None:
            if not await self.authors_repo.get_author(book_update.author_id):
                return None

        await FastAPICache.clear(namespace=settings.cache.namespace.books.books_list)
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.books.book}:{book_id}"
        )

        book = await self.get_book(book_id)

        if not book:
            return None

        for name, value in book_update.model_dump(exclude_unset=partial).items():
            setattr(book, name, value)

        await self.db.commit()
        await self.db.refresh(book)

        logger.info("Successfully updated book: %s", book.id)
        return book

    async def delete_book(self, book_id: int) -> bool:
        logger.info("Deleting book: %s", book_id)

        await FastAPICache.clear(namespace=settings.cache.namespace.books.books_list)
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.books.book}:{book_id}"
        )

        book = await self.get_book(book_id)

        if not book:
            return False

        await self.db.delete(book)
        await self.db.commit()

        logger.info(f"Book deleted successfully: {book_id}")
        return True

    async def delete_all_books(self) -> bool:
        logger.info("Deleting all books")

        await FastAPICache.clear(namespace=settings.cache.namespace.books.books_list)

        command = text("TRUNCATE TABLE bookmodels RESTART IDENTITY CASCADE")

        await self.db.execute(command)
        await self.db.commit()

        logger.info("All books deleted successfully")
        return True
