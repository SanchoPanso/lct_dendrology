# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Установка Poetry
ENV POETRY_VERSION=2.2.1
RUN pip install "poetry==$POETRY_VERSION"

# Создание рабочей директории
WORKDIR /app

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости через poetry
RUN poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi

# Копируем весь проект
COPY . .
