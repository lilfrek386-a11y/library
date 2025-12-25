from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi_cache.decorator import cache

from src.core.utils import custom_key_builder
from src.core.config import settings
from .schemas import BookId, BookUpdatePartial, BookUpdate, BookCreate
from .dependencies import get_book_service
from .service import BooksService

router = APIRouter(prefix="/books", tags=["Книги"])


@router.get("/", summary="Отримати усі книжки", response_model=list[BookId])
@cache(
    expire=60,
    namespace=settings.cache.namespace.books.books_list,
    key_builder=custom_key_builder,
)
async def get_books(
    book_service: Annotated[BooksService, Depends(get_book_service)],
) -> list[BookId]:
    return await book_service.get_books()


@router.get("/{book_id}", summary="Отримати одну книгу", response_model=BookId)
@cache(
    expire=60,
    namespace=settings.cache.namespace.books.book,
    key_builder=custom_key_builder,
)
async def get_book(
    book_id: int,
    book_service: Annotated[BooksService, Depends(get_book_service)],
) -> BookId:
    return await book_service.get_book(book_id)


@router.post(
    "/",
    summary="Додати книгу",
    response_model=BookId,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    new_book: BookCreate,
    book_service: Annotated[BooksService, Depends(get_book_service)],
) -> BookId:
    return await book_service.create_book(new_book=new_book)


@router.put(
    "/{book_id}",
    summary="Оновити повністью книгу",
    response_model=BookId,
)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    book_service: Annotated[BooksService, Depends(get_book_service)],
) -> BookId:
    return await book_service.update_book(book_id=book_id, book_update=book_update)


@router.patch(
    "/{book_id}",
    summary="Часткове оновлення книги",
    response_model=BookId,
)
async def update_book_partial(
    book_id: int,
    book_update: BookUpdatePartial,
    book_service: Annotated[BooksService, Depends(get_book_service)],
) -> BookId:
    return await book_service.update_book(
        book_id=book_id, book_update=book_update, partial=True
    )


@router.delete(
    "/{book_id}", summary="Видалити одну книгу", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_book(
    book_id: int,
    book_service: Annotated[BooksService, Depends(get_book_service)],
) -> None:
    await book_service.delete_book(book_id)


@router.delete(
    "/", summary="Видалити всі книги", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_books(
    book_service: Annotated[BooksService, Depends(get_book_service)],
) -> None:
    await book_service.delete_all_books()
