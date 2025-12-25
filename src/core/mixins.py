from typing import TypeVar, Optional
from fastapi import HTTPException, status

T = TypeVar("T")


class ServiceMixin:
    @staticmethod
    def get_or_404(obj: Optional[T], detail: str = "Entity not found") -> T:
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        return obj
