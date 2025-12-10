from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from .base_model import Base

if TYPE_CHECKING:
    from .author import AuthorModel


class BookModel(Base):
    __tablename__ = "books"

    title: Mapped[str]
    year: Mapped[int]
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE")
    )

    author: Mapped["AuthorModel"] = relationship(back_populates="books")
