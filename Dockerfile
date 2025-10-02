# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Установка Poetry
ENV POETRY_VERSION=2.2.1
RUN pip3 install "poetry==$POETRY_VERSION" && poetry config virtualenvs.create false

# Создание рабочей директории
WORKDIR /app

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml ./

# Устанавливаем зависимости через poetry
ARG POETRY_GROUPS="test"
RUN poetry install --no-root
RUN poetry install --extras ${POETRY_GROUPS} --no-root

# Копируем весь проект
COPY . .
RUN poetry install --only-root
