import logging
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.authors.service import AuthorsService
from src.core.db import db_helper
from src.api_v1.authors.repository import AuthorsRepository

logger = logging.getLogger(__name__)


def get_author_repository(
    db: AsyncSession = Depends(db_helper.session_dependency),
) -> AuthorsRepository:
    return AuthorsRepository(db)


def get_author_service(
    author_repository: AuthorsRepository = Depends(get_author_repository),
):
    return AuthorsService(author_repository)
