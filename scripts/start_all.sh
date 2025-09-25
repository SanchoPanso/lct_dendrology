#!/bin/bash

# Скрипт для одновременного запуска FastAPI сервера и Telegram бота
# Автор: LCT Dendrology Project

set -e  # Остановить выполнение при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия .env файла
check_env_file() {
    if [ ! -f ".env" ]; then
        log_warning "Файл .env не найден!"
        log_info "Создайте файл .env в корне проекта с переменными:"
        echo "TELEGRAM_BOT_TOKEN=your_bot_token_here"
        echo "SERVER_URL=http://localhost:8000"
        echo "SERVER_PORT=8000"
        echo "REQUEST_TIMEOUT=30"
        exit 1
    fi
}

# Проверка активации виртуального окружения
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "Виртуальное окружение не активировано!"
        log_info "Активируйте виртуальное окружение:"
        echo "source venv/bin/activate"
        exit 1
    fi
}

# Функция для остановки всех процессов
cleanup() {
    log_info "Останавливаем все процессы..."
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null || true
    fi
    exit 0
}

# Устанавливаем обработчик сигналов для корректного завершения
trap cleanup SIGINT SIGTERM

# Основная функция
main() {
    log_info "Запуск LCT Dendrology системы..."
    
    # Проверки
    check_env_file
    check_venv
    
    # Загружаем переменные окружения
    source .env
    
    log_info "Переменные окружения загружены"
    
    # Проверяем наличие токена бота
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        log_error "TELEGRAM_BOT_TOKEN не установлен в .env файле!"
        exit 1
    fi
    
    log_success "Все проверки пройдены"
    
    # Запускаем сервер в фоне
    log_info "Запуск FastAPI сервера..."
    python examples/run_server.py &
    SERVER_PID=$!
    log_success "Сервер запущен (PID: $SERVER_PID)"
    
    # Ждем запуска сервера
    log_info "Ожидание запуска сервера..."
    sleep 3
    
    # Проверяем, что сервер запустился
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        log_error "Сервер не запустился!"
        exit 1
    fi
    
    log_success "Сервер готов к работе"
    
    # Запускаем бота
    log_info "Запуск Telegram бота..."
    python examples/run_bot.py &
    BOT_PID=$!
    log_success "Бот запущен (PID: $BOT_PID)"
    
    # Выводим информацию о запущенных процессах
    echo ""
    log_success "Система запущена успешно!"
    echo ""
    echo "FastAPI сервер: http://localhost:${SERVER_PORT:-8000}"
    echo "API документация: http://localhost:${SERVER_PORT:-8000}/docs"
    echo "Telegram бот: @$(python -c "import os; print(os.getenv('TELEGRAM_BOT_TOKEN', '').split(':')[0])" 2>/dev/null || echo "your_bot_name")"
    echo ""
    echo "Для остановки нажмите Ctrl+C"
    echo ""
    
    # Ждем завершения процессов
    wait $SERVER_PID $BOT_PID
}

# Запуск основной функции
main "$@"
