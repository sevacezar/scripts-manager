# Scripts Manager

REST API сервис для выполнения Python скриптов с гибкой передачей данных и файловым хранилищем.

## Описание

Scripts Manager позволяет выполнять Python скрипты через REST API, передавая данные в формате JSON. Сервис разработан для интеграции с ПО для гидродинамического моделирования, где Python интерпретатор имеет ограниченный набор библиотек.

## Основные возможности

- ✅ Выполнение Python скриптов через REST API (JSON in/out)
- ✅ Файловое хранилище с S3-совместимым интерфейсом
- ✅ Безопасное выполнение скриптов (валидация путей, таймауты)
- ✅ Структурированное логирование (structlog)
- ✅ Гибкая архитектура (можно подключить S3 вместо локального хранилища)

## Требования

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) - быстрый менеджер пакетов Python

## Установка uv

### Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Альтернативные способы

- Через pip: `pip install uv`
- Через Homebrew: `brew install uv`
- Через Cargo: `cargo install uv`

Проверка установки:
```bash
uv --version
```

## Установка проекта

```bash
# Клонирование репозитория (если применимо)
git clone <repository-url>
cd scripts_manager

# Установка зависимостей через uv
uv pip install -e .

# Или создание виртуального окружения и установка
uv venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows
uv pip install -e .
```

## Запуск

```bash
# Запуск сервера разработки
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Или через Python
python -m uvicorn src.app:app --reload

# Или через uv
uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

После запуска документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Выполнение скриптов

#### POST `/api/v1/scripts/{script_path}`

Выполняет Python скрипт по указанному пути.

**Требования к скрипту:**
- Должен быть одним файлом `.py`
- Должен содержать функцию `main(data: dict) -> dict`
- Функция получает JSON данные как словарь
- Функция должна возвращать словарь (или `None`, что станет пустым `{}`)

**Параметры:**
- `script_path` (path): Относительный путь к скрипту от папки `scripts/`

**Тело запроса (JSON):**
```json
{
  "data": {
    "key1": "value1",
    "key2": {"nested": "data"},
    "file_key": "prefix/filename.txt"
  }
}
```

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_args_in_request_args_in_response.py" \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "John", "value": 42}}'
```

**Ответ:**
```json
{
  "success": true,
  "result": {
    "message": "Hello, John!",
    "processed_value": 84
  },
  "execution_time": 0.123
}
```

### Файловое хранилище

#### POST `/api/v1/files/upload`

Загружает файл в хранилище и возвращает ключ для доступа.

**Параметры:**
- `file` (form-data): Файл для загрузки
- `prefix` (query, optional): Префикс для организации файлов (как в S3)

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload?prefix=test" \
  -F "file=@data.txt"
```

**Ответ:**
```json
{
  "key": "test/aBc123XyZ456.txt",
  "size": 1234
}
```

#### GET `/api/v1/files/{key}`

Скачивает файл по ключу.

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/files/test/aBc123XyZ456.txt" \
  --output downloaded_file.txt
```

#### GET `/api/v1/files/{key}/info`

Получает информацию о файле без скачивания.

**Пример запроса:**
```bash
curl "http://localhost:8000/api/v1/files/test/aBc123XyZ456.txt/info"
```

**Ответ:**
```json
{
  "key": "test/aBc123XyZ456.txt",
  "size": 1234,
  "content_type": "text/plain"
}
```

#### DELETE `/api/v1/files/{key}`

Удаляет файл по ключу.

**Пример запроса:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/files/test/aBc123XyZ456.txt"
```

## Как писать скрипты

### Структура скрипта

Каждый скрипт должен содержать функцию `main()`, которая принимает словарь с данными и возвращает словарь с результатом:

```python
def main(data: dict) -> dict:
    """
    Main function that processes input data.
    
    Args:
        data: Input JSON data as dictionary
        
    Returns:
        Dictionary with processed result
    """
    # Извлечение данных
    name: str = data.get("name", "Unknown")
    value: int = data.get("value", 0)
    
    # Обработка данных
    result: dict = {
        "message": f"Hello, {name}!",
        "processed_value": value * 2,
    }
    
    return result
```

### Работа с файлами

Для работы с файлами используйте файловое хранилище:

1. **Загрузите файл** через API `/api/v1/files/upload` и получите ключ
2. **Передайте ключ** в JSON данных при выполнении скрипта
3. **В скрипте** используйте ключ для доступа к файлу (через API или клиент хранилища)

**Пример скрипта с файлом:**
```python
def main(data: dict) -> dict:
    # Получаем ключ файла из входных данных
    file_key: str | None = data.get("file_key")
    
    if not file_key:
        return {"error": "file_key is required"}
    
    # В реальном сценарии здесь можно:
    # 1. Использовать клиент файлового хранилища для скачивания
    # 2. Обработать файл
    # 3. Сохранить результат обратно в хранилище
    
    return {
        "message": f"Processing file: {file_key}",
        "status": "success"
    }
```

### Полный пример

```python
"""Example script for processing data."""

def main(data: dict) -> dict:
    """
    Process input data and return result.
    
    Args:
        data: Input JSON data
        
    Returns:
        Processed result as dictionary
    """
    # Extract input data
    name: str = data.get("name", "Unknown")
    file_key: str | None = data.get("file_key")
    
    # Process data
    result: dict = {
        "message": f"Hello, {name}!",
        "file_processed": file_key is not None,
    }
    
    # If file key provided, add file info
    if file_key:
        result["file_key"] = file_key
        result["note"] = "Download file using /api/v1/files/{key} endpoint"
    
    return result
```

## Структура проекта

```
scripts_manager/
├── src/
│   ├── app.py                      # Главное приложение FastAPI
│   ├── config.py                    # Конфигурация
│   ├── logger.py                    # Настройка логирования
│   ├── file_storage/
│   │   ├── __init__.py              # Экспорт классов
│   │   ├── client.py                # Протокол и LocalFileStorage
│   │   ├── router.py                # Эндпойнты для файлов
│   │   └── schemas.py               # Схемы для файлового API
│   └── script_executor/
│       ├── router.py                # Эндпойнт выполнения скриптов
│       ├── service.py               # Сервис выполнения (через main())
│       └── schemas.py               # Схемы запросов/ответов
├── scripts/                         # Директория со скриптами
│   ├── test/                        # Тестовые скрипты
│   ├── hydrodynamics/               # Скрипты для гидродинамики
│   └── geology/                     # Скрипты для геологии
├── uploads/                         # Локальное файловое хранилище
├── pyproject.toml                   # Зависимости проекта
└── README.md                         # Документация
```

## Безопасность

- ✅ Валидация путей скриптов (защита от path traversal)
- ✅ Ограничение времени выполнения скриптов
- ✅ Ограничение размера загружаемых файлов
- ✅ Проверка расширений файлов
- ✅ Изоляция выполнения скриптов (subprocess)
- ✅ Генерация случайных имен файлов (избежание коллизий)

## Конфигурация

Настройки можно изменить в `src/config.py` или через переменные окружения:

- `SCRIPTS_DIR` - директория со скриптами
- `UPLOADS_DIR` - директория для файлового хранилища
- `MAX_SCRIPT_EXECUTION_TIME` - максимальное время выполнения (секунды, по умолчанию 300)
- `MAX_FILE_SIZE` - максимальный размер файла (байты, по умолчанию 100MB)
- `DEBUG` - режим отладки
- `LOG_LEVEL` - уровень логирования (по умолчанию INFO)
- `ENVIRONMENT` - окружение (development/production)

## Примеры использования

### Пример 1: Простая обработка данных

**Скрипт:** `scripts/test/test_args_in_request_args_in_response.py`

```python
def main(data: dict) -> dict:
    name = data.get("name", "Unknown")
    value = data.get("value", 0)
    return {
        "message": f"Hello, {name}!",
        "processed_value": value * 2,
    }
```

**Запрос:**
```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_args_in_request_args_in_response.py" \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "World", "value": 42}}'
```

### Пример 2: Работа с файлами

**Шаг 1: Загрузка файла**
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload?prefix=test" \
  -F "file=@data.txt"
# Response: {"key": "test/aBc123XyZ456.txt", "size": 1234}
```

**Шаг 2: Выполнение скрипта с файлом**
```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_file_in_request_file_in_response.py" \
  -H "Content-Type: application/json" \
  -d '{"data": {"file_key": "test/aBc123XyZ456.txt"}}'
```

**Шаг 3: Скачивание результата (если скрипт вернул file_key)**
```bash
curl "http://localhost:8000/api/v1/files/test/result_xyz789.txt"
```

## Разработка

### Добавление нового скрипта

1. Создайте файл в директории `scripts/` (например, `scripts/my_script.py`)
2. Напишите функцию `main(data: dict) -> dict`
3. Вызовите скрипт через API: `POST /api/v1/scripts/my_script.py`

### Тестирование

```bash
# Запуск тестовых скриптов
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_args_in_request_args_in_response.py" \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "Test", "value": 123}}'
```

### Использование uv для разработки

```bash
# Установка зависимостей
uv pip install -e .

# Запуск с uv
uv run uvicorn src.app:app --reload

# Добавление новой зависимости
uv pip install package-name
uv pip freeze > requirements.txt  # если нужно
```

## Расширение функциональности

### Подключение S3 вместо локального хранилища

Создайте реализацию `FileStorageClient` для S3:

```python
from src.file_storage import FileStorageClient
import boto3

class S3FileStorage(FileStorageClient):
    async def save_file(self, file_content: bytes, prefix: str = "", filename: str | None = None) -> str:
        # Реализация для S3
        pass
    
    # ... остальные методы
```

Затем замените `LocalFileStorage` на `S3FileStorage` в `src/file_storage/router.py`.

## Лицензия

MIT
