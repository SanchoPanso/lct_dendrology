## LCT Dendrology Telegram Bot

### Возможности
- Принимает изображения (сообщения с фото)
- Возвращает текст-заглушку

### Установка и запуск (Poetry)
1. Создайте окружение и установите Poetry (если ещё не установлено):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install poetry
   poetry config virtualenvs.in-project true
   ```
2. Установите зависимости:
   ```bash
   poetry install
   ```
3. Создайте файл `.env` в корне проекта и укажите настройки:
   ```bash
   # Основные настройки
   TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   LOG_LEVEL=INFO
   ```
4. Запустите бота:
   ```bash
   poetry run python examples/run_bot.py
   ```
5. Запустите сервер (в отдельном терминале):
   ```bash
   poetry run python examples/run_server.py
   ```

### Конфигурация

Проект использует `pydantic-settings` для управления настройками. Все настройки загружаются из:
- Переменных окружения
- Файла `.env` (если существует)
- Значений по умолчанию

Основные настройки:
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота (обязательно)
- `BACKEND_HOST` - хост для FastAPI сервера (по умолчанию: 0.0.0.0)
- `BACKEND_PORT` - порт для FastAPI сервера (по умолчанию: 8000)
- `LOG_LEVEL` - уровень логирования (по умолчанию: INFO)

Полный список настроек доступен в `lct_dendrology/cfg/settings.py`.

### Примечания
- Текущая логика отвечает заглушкой и не анализирует изображение.



