from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=0, le=2025)
    author_id: int
    model_config = ConfigDict(extra="forbid")

    def __str__(self):
        return f"{self.title} {self.year}"


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookUpdatePartial(BaseModel):
    title: str | None = None
    year: int | None = None
    author_id: int | None = None
    model_config = ConfigDict(extra="forbid")


class BookId(BookBase):
    id: int
