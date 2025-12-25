import logging
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.books.service import BooksService
from src.api_v1.authors.repository import AuthorsRepository
from src.api_v1.books.repository import BooksRepository
from src.core.db import db_helper
from src.api_v1.authors.dependencies import get_author_repository

logger = logging.getLogger(__name__)


def get_book_repository(
    db: AsyncSession = Depends(db_helper.session_dependency),
) -> BooksRepository:
    return BooksRepository(db)


def get_book_service(
    book_repo: BooksRepository = Depends(get_book_repository),
    author_repo: AuthorsRepository = Depends(get_author_repository),
):
    return BooksService(book_repo, author_repo)
