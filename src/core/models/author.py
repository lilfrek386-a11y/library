from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base_model import Base


if TYPE_CHECKING:
    from .book import BookModel


class AuthorModel(Base):
    __tablename__ = "authors"

    first_name: Mapped[str] = mapped_column(String(32))
    last_name: Mapped[str] = mapped_column(String(32))
    age: Mapped[int]
    bio: Mapped[str | None] = None
    email: Mapped[str]

    books: Mapped[list["BookModel"]] = relationship(
        back_populates="author", passive_deletes=True
    )
