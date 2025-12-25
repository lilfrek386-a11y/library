from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi_cache.decorator import cache

from src.core.utils import custom_key_builder
from src.core.config import settings
from .dependencies import get_author_service
from .schemas import AuthorId, AuthorUpdate, AuthorUpdatePartial, AuthorCreate
from .service import AuthorsService

router = APIRouter(prefix="/authors", tags=["Автори"])


@router.get("/{author_id}", summary="Отримати одного автора", response_model=AuthorId)
@cache(
    expire=60,
    key_builder=custom_key_builder,
    namespace=settings.cache.namespace.authors.author,
)
async def get_author(
    author_id: int,
    author_service: Annotated[AuthorsService, Depends(get_author_service)],
) -> AuthorId:
    return await author_service.get_author(author_id)


@router.get("/", summary="Отримати всіх авторів", response_model=list[AuthorId])
@cache(
    expire=60,
    key_builder=custom_key_builder,
    namespace=settings.cache.namespace.authors.authors_list,
)
async def get_authors(
    author_service: Annotated[AuthorsService, Depends(get_author_service)],
) -> list[AuthorId]:
    return await author_service.get_authors()


@router.post(
    "/",
    summary="Додати автора",
    response_model=AuthorId,
    status_code=status.HTTP_201_CREATED,
)
async def create_author(
    new_author: AuthorCreate,
    author_service: Annotated[AuthorsService, Depends(get_author_service)],
) -> AuthorId:
    return await author_service.create_author(new_author)


@router.put("/{author_id}", summary="Оновити дані про автора", response_model=AuthorId)
async def update_author(
    author_id: int,
    author_update: AuthorUpdate,
    author_service: Annotated[AuthorsService, Depends(get_author_service)],
) -> AuthorId:
    return await author_service.update_author(author_id, author_update)


@router.patch(
    "/{author_id}", summary="Оновити частково дані про автора", response_model=AuthorId
)
async def update_author_partial(
    author_id: int,
    author_update: AuthorUpdatePartial,
    author_service: Annotated[AuthorsService, Depends(get_author_service)],
) -> AuthorId:
    return await author_service.update_author(author_id, author_update, partial=True)


@router.delete(
    "/{author_id}",
    summary="Видалити одного автора",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_author(
    author_id: int,
    author_service: Annotated[AuthorsService, Depends(get_author_service)],
) -> None:
    await author_service.delete_author(author_id)


@router.delete(
    "/",
    summary="Видалити всіх авторів з таблиці",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_authors(
    author_service: Annotated[AuthorsService, Depends(get_author_service)],
) -> None:
    await author_service.delete_all_authors()
