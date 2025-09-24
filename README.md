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
3. Создайте файл `.env` в корне проекта и укажите токен бота:
   ```bash
   echo "TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN" > .env
   ```
4. Запустите пример:
   ```bash
   poetry run python examples/run_bot.py
   ```

### Примечания
- Текущая логика отвечает заглушкой и не анализирует изображение.



