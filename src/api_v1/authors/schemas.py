from pydantic import BaseModel, Field, EmailStr, ConfigDict


class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    age: int = Field(ge=0, le=135)
    bio: str | None = Field(None, max_length=1000)
    email: EmailStr
    model_config = ConfigDict(extra="forbid")

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.age} years old"


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    pass


class AuthorUpdatePartial(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = Field(None, ge=0, le=135)
    bio: str | None = Field(None, max_length=1000)
    email: EmailStr | None = None


class AuthorId(AuthorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
