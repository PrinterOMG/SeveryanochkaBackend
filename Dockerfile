FROM python:3.11
LABEL authors="printeromg"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_CACHE_DIR='/var/cache/pypoetry'
ENV POETRY_HOME='/usr/local'
ENV POETRY_VERSION=1.7.1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install curl build-essential -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app/

COPY pyproject.toml .
RUN poetry install --only=main --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
