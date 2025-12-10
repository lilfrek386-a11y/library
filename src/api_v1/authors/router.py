from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi_cache.decorator import cache

from src.api_v1.authors.author_repository import AuthorsRepository
from .dependencies import get_author_repository
from .schemas import AuthorId, AuthorUpdate, AuthorUpdatePartial, AuthorCreate
from src.core.utils import custom_key_builder
from src.core.config import settings

router = APIRouter(prefix="/authors", tags=["Автори"])


@router.get("/{author_id}", summary="Отримати одного автора", response_model=AuthorId)
@cache(
    expire=60,
    key_builder=custom_key_builder,
    namespace=settings.cache.namespace.authors.author,
)
async def get_author(
    author_id: int,
    author_repo: Annotated["AuthorsRepository", Depends(get_author_repository)],
) -> AuthorId | None:
    author = await author_repo.get_author(author_id)

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )
    author_dto = AuthorId.model_validate(author)
    return author_dto


@router.get("/", summary="Отримати всіх авторів", response_model=list[AuthorId])
@cache(
    expire=60,
    key_builder=custom_key_builder,
    namespace=settings.cache.namespace.authors.authors_list,
)
async def get_authors(
    author_repo: Annotated["AuthorsRepository", Depends(get_author_repository)],
) -> list[AuthorId]:
    authors = await author_repo.get_authors()

    authors_dto = [AuthorId.model_validate(a) for a in authors]

    return authors_dto


@router.post(
    "/",
    summary="Додати автора",
    response_model=AuthorId,
    status_code=status.HTTP_201_CREATED,
)
async def create_author(
    new_author: AuthorCreate,
    author_repo: Annotated["AuthorsRepository", Depends(get_author_repository)],
) -> AuthorId:

    author = await author_repo.create_author(new_author)

    author_dto = AuthorId.model_validate(author)
    return author_dto


@router.put("/{author_id}", summary="Оновити дані про автора")
async def update_author(
    author_id: int,
    author_update: AuthorUpdate,
    author_repo: Annotated["AuthorsRepository", Depends(get_author_repository)],
) -> AuthorId:

    author = await author_repo.update_author(author_id, author_update)

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )

    author_dto = AuthorId.model_validate(author)

    return author_dto


@router.patch(
    "/{author_id}", summary="Оновити частково дані про автора", response_model=AuthorId
)
async def update_author_partial(
    author_id: int,
    author_update: AuthorUpdatePartial,
    author_repo: Annotated["AuthorsRepository", Depends(get_author_repository)],
) -> AuthorId:
    author = await author_repo.update_author(author_id, author_update, partial=True)

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )

    author_dto = AuthorId.model_validate(author)

    return author_dto


@router.delete(
    "/{author_id}",
    summary="Видалити одного автора",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def author_delete(
    author_id: int,
    author_repo: Annotated["AuthorsRepository", Depends(get_author_repository)],
):
    author_op_delete = await author_repo.delete_author(author_id)
    if not author_op_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
        )


@router.delete(
    "/",
    summary="Видалити всіх авторів з таблиці",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def authors_delete(
    author_repo: Annotated["AuthorsRepository", Depends(get_author_repository)],
):
    return await author_repo.delete_all_authors()
