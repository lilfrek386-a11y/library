FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /library

RUN pip install --upgrade pip wheel poetry

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./

COPY logging.ini alembic.ini ./

COPY alembic ./alembic

RUN poetry install --no-root

COPY src ./src

RUN chmod +x src/prestart.sh

ENTRYPOINT ["./src/prestart.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]