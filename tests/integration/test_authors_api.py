import random
import string

import pytest
from httpx import AsyncClient

from src.api_v1.authors.schemas import AuthorId


@pytest.mark.parametrize(
    "author, status_code",
    [
        (
            {
                "first_name": "Alexander",
                "last_name": "Pushkin",
                "email": "pushkin@example.com",
                "age": 35,
            },
            201,
        ),
        (
            {
                "first_name": "P",
                "last_name": "",
                "email": "pushkin@example.com",
                "age": 35,
            },
            422,
        ),
        (
            {
                "first_name": "jklP",
                "last_name": "phj",
                "email": "pushkin@example.com",
                "age": -56,
            },
            422,
        ),
        (
            {
                "first_name": "jklP",
                "last_name": "phj",
                "email": "pushkin@example.com",
                "age": 9,
                "bio": "".join(random.choices(string.ascii_letters, k=1555)),
            },
            422,
        ),
    ],
)
async def test_create_authors(ac: AsyncClient, author: dict, status_code: int):
    response = await ac.post(
        "/authors/",
        json=author,
    )

    assert response.status_code == status_code
