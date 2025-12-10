import logging
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.authors.author_repository import AuthorsRepository
from src.api_v1.books.book_repository import BookRepository
from src.core.db import db_helper
from src.api_v1.authors.dependencies import get_author_repository

logger = logging.getLogger(__name__)


def get_book_repository(
    db: AsyncSession = Depends(db_helper.session_dependency),
    author_repo: AuthorsRepository = Depends(get_author_repository),
) -> BookRepository:
    return BookRepository(db, author_repo)


