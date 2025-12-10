import hashlib
from starlette.requests import Request
from fastapi_cache import FastAPICache


async def custom_key_builder(
    func,
    namespace: str,
    request: Request,
    response=None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()

    def clean_value(v):
        if isinstance(v, (str, int, float, bool, type(None))):
            return v

        if hasattr(v, "model_dump"):
            return v.model_dump()

        return f"<obj:{v.__class__.__name__}>"

    clean_kwargs = {k: clean_value(v) for k, v in kwargs.items()}

    path_params = {k: clean_value(v) for k, v in request.path_params.items()}

    element_id = request.path_params.get("author_id") or request.path_params.get(
        "book_id"
    )
    raw_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{path_params}:{clean_kwargs}"
    hash_part = hashlib.md5(raw_key.encode()).hexdigest()
    if element_id:
        return f"{namespace}:{element_id}:{hash_part}"

    return f"{namespace}:{hash_part}"
