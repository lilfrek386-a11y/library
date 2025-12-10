from fastapi import APIRouter, HTTPException, status, Depends
import logging

from fastapi_cache.decorator import cache

from src.core.utils import custom_key_builder
from src.core.config import settings
from .schemas import BookId, BookUpdatePartial, BookUpdate, BookCreate
from .book_repository import BookRepository
from .dependencies import get_book_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/books", tags=["Книги"])


@router.get("/", summary="Отримати усі книжки", response_model=list[BookId])
@cache(
    expire=60,
    namespace=settings.cache.namespace.books.books_list,
    key_builder=custom_key_builder,
)
async def get_books(book_repo: BookRepository = Depends(get_book_repository)):
    books = await book_repo.get_books()

    return [BookId.model_validate(book, from_attributes=True) for book in books]


@router.get("/{book_id}", summary="Отримати одну книгу", response_model=BookId)
@cache(
    expire=60,
    namespace=settings.cache.namespace.books.book,
    key_builder=custom_key_builder,
)
async def get_book(
    book_id: int,
    book_repo: BookRepository = Depends(get_book_repository),
):
    book = await book_repo.get_book(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено",
        )

    return BookId.model_validate(book, from_attributes=True)


@router.post(
    "/",
    summary="Додати книгу",
    response_model=BookId,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    new_book: BookCreate,
    book_repo: BookRepository = Depends(get_book_repository),
) -> BookId:
    created_book = await book_repo.create_book(new_book=new_book)

    if not created_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неможливо створити книгу. Перевірте валідність введених данних.",
        )

    return BookId.model_validate(created_book, from_attributes=True)


@router.put(
    "/{book_id}",
    summary="Оновити повністью книгу",
    response_model=BookId,
)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    book_repo: BookRepository = Depends(get_book_repository),
) -> BookId:
    updated_book = await book_repo.update_book(book_id=book_id, book_update=book_update)

    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено або вказаного автора не існує.",
        )

    return BookId.model_validate(updated_book, from_attributes=True)


@router.patch(
    "/{book_id}",
    summary="Часткове оновлення книги",
    response_model=BookId,
)
async def update_book_partial(
    book_id: int,
    book_update: BookUpdatePartial,
    book_repo: BookRepository = Depends(get_book_repository),
) -> BookId:
    updated_book = await book_repo.update_book(
        book_id=book_id, book_update=book_update, partial=True
    )

    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено або вказаного автора не існує.",
        )

    return BookId.model_validate(updated_book, from_attributes=True)


@router.delete(
    "/{book_id}", summary="Видалити одну книгу", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_book(
    book_id: int,
    book_repo: BookRepository = Depends(get_book_repository),
):
    success = await book_repo.delete_book(book_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з ID {book_id} не знайдено, видалення неможливе.",
        )

    return None


@router.delete(
    "/", summary="Видалити всі книги", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_books(book_repo: BookRepository = Depends(get_book_repository)):
    await book_repo.delete_all_books()
    return None
