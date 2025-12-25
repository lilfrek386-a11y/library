import logging

from fastapi import HTTPException, status
from fastapi_cache import FastAPICache

from src.api_v1.books.repository import BooksRepository
from src.core.mixins import ServiceMixin
from src.core.config import settings
from src.api_v1.books.repository import AuthorsRepository
from src.api_v1.books.schemas import *

logger = logging.getLogger(__name__)


class BooksService(ServiceMixin):
    def __init__(self, books_repo: BooksRepository, authors_repo: AuthorsRepository):
        self.authors_repo = authors_repo
        self.books_repo = books_repo

    async def get_books(self) -> list[BookId]:
        logger.info("Get all books")
        books = await self.books_repo.get_all()
        return [BookId.model_validate(x) for x in books]

    async def get_book(self, book_id: int) -> BookId:
        logger.info(f"Get book %s", book_id)

        book = self.get_or_404(
            await self.books_repo.get_one(book_id), detail="Book not found"
        )

        return BookId.model_validate(book)

    async def create_book(self, new_book: BookCreate) -> BookId:
        logger.info("Creating book with data: %s", new_book)

        author = await self.authors_repo.get_one(new_book.author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with id {new_book.author_id} not found",
            )

        book = await self.books_repo.create(new_book.model_dump())

        await FastAPICache.clear(namespace=settings.cache.namespace.books.books_list)
        return BookId.model_validate(book)

    async def update_book(
        self,
        book_id: int,
        book_update: BookUpdate | BookUpdatePartial,
        partial: bool = False,
    ) -> BookId:

        book = self.get_or_404(
            await self.books_repo.get_one(book_id), detail="Book not found"
        )

        if book_update.author_id is not None:
            author = await self.authors_repo.get_one(book_update.author_id)
            if not author:
                raise HTTPException(status_code=404, detail="New author not found")

        update_data = book_update.model_dump(exclude_unset=partial)

        updated_book = await self.books_repo.update(
            db_obj=book, update_data=update_data
        )

        await FastAPICache.clear(namespace=settings.cache.namespace.books.books_list)
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.books.book}:{book_id}"
        )

        return BookId.model_validate(updated_book)

    async def delete_book(self, book_id: int) -> None:
        logger.info(f"Deleting book %s", book_id)

        book = self.get_or_404(
            await self.books_repo.get_one(book_id), detail="Book not found"
        )

        await self.books_repo.delete(book)

        await FastAPICache.clear(
            namespace=settings.cache.namespace.books.books_list,
        )
        await FastAPICache.clear(
            namespace=f"{settings.cache.namespace.books.book}:{book_id}"
        )

    async def delete_all_books(self):
        logger.info(f"Delete all books")

        await self.books_repo.delete_all_books()

        await FastAPICache.clear(namespace=settings.cache.namespace.books.books_list)
