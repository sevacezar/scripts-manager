# Scripts Manager

REST API сервис для управления и выполнения Python скриптов с гибкой передачей данных, файловым хранилищем и системой управления скриптами через веб-интерфейс.

## Описание

Scripts Manager — это комплексное решение для управления Python скриптами через REST API. Сервис позволяет:
- Выполнять Python скрипты, передавая данные в формате JSON
- Управлять скриптами и папками через веб-интерфейс (создание, редактирование, удаление)
- Организовывать скрипты в иерархическую структуру папок
- Работать с файловым хранилищем для передачи файлов в скрипты

Сервис разработан для интеграции с ПО для гидродинамического моделирования, где Python интерпретатор имеет ограниченный набор библиотек.

## Основные возможности

- ✅ **Управление скриптами и папками** — создание, редактирование, удаление через REST API
- ✅ **Иерархическая организация** — структурирование скриптов в папки и подпапки
- ✅ **Выполнение Python скриптов** через REST API (JSON in/out)
- ✅ **Аутентификация и авторизация** — JWT токены, контроль доступа к ресурсам
- ✅ **Файловое хранилище** с S3-совместимым интерфейсом
- ✅ **Безопасное выполнение скриптов** (валидация путей, таймауты)
- ✅ **Структурированное логирование** (structlog)
- ✅ **Единый формат ошибок** с кодами для программной обработки
- ✅ **Гибкая архитектура** (можно подключить S3 вместо локального хранилища)

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

**Подробная документация API для фронтенд-разработчиков:**
- [API Documentation](./src/scripts_manager/API_DOCUMENTATION.md) — полная документация всех эндпойнтов управления скриптами и папками

## Аутентификация

Большинство эндпойнтов требуют аутентификации через JWT токен. Для получения токена используйте эндпойнты `/api/v1/auth/register` и `/api/v1/auth/login`.

**Формат заголовка:**
```
Authorization: Bearer <access_token>
```

### Регистрация пользователя

**POST** `/api/v1/auth/register`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"login": "user123", "password": "secure_password"}'
```

### Вход в систему

**POST** `/api/v1/auth/login`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "user123", "password": "secure_password"}'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Используйте `access_token` в заголовке `Authorization` для всех последующих запросов.

## API Endpoints

### Управление скриптами и папками

Система управления скриптами позволяет создавать иерархическую структуру папок, загружать скрипты, редактировать их метаданные и управлять правами доступа.

**Базовый путь:** `/api/v1/scripts-manager`

#### Основные возможности:

- **Папки:**
  - `POST /api/v1/scripts-manager/folders` — создание папки
  - `GET /api/v1/scripts-manager/folders/{folder_id}` — получение информации о папке
  - `PUT /api/v1/scripts-manager/folders/{folder_id}` — переименование папки
  - `DELETE /api/v1/scripts-manager/folders/{folder_id}` — удаление папки со всем содержимым

- **Скрипты:**
  - `POST /api/v1/scripts-manager/scripts` — загрузка нового скрипта
  - `GET /api/v1/scripts-manager/scripts/{script_id}` — получение информации о скрипте
  - `GET /api/v1/scripts-manager/scripts/{script_id}/content` — получение исходного кода скрипта
  - `PUT /api/v1/scripts-manager/scripts/{script_id}` — обновление метаданных скрипта
  - `DELETE /api/v1/scripts-manager/scripts/{script_id}` — удаление скрипта

- **Дерево структуры:**
  - `GET /api/v1/scripts-manager/tree` — получение полной иерархии всех папок и скриптов

**Пример создания папки и загрузки скрипта:**

```bash
# 1. Создать папку
curl -X POST "http://localhost:8000/api/v1/scripts-manager/folders" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "geology", "parent_id": null}'

# 2. Загрузить скрипт в папку
curl -X POST "http://localhost:8000/api/v1/scripts-manager/scripts" \
  -H "Authorization: Bearer <token>" \
  -F "file=@script.py" \
  -F "display_name=Analysis Script" \
  -F "description=Script for data analysis" \
  -F "folder_id=1" \
  -F "replace=false"
```

**Важно:** При загрузке скрипта, который уже существует, API вернет ошибку `SCRIPT_EXISTS_REPLACE_REQUIRED`. Фронтенд должен обработать это и предложить пользователю перезаписать скрипт, отправив запрос с `replace=true`.

**Подробная документация:** См. [API_DOCUMENTATION.md](./src/scripts_manager/API_DOCUMENTATION.md) для полного описания всех эндпойнтов, форматов запросов/ответов и обработки ошибок.

### Выполнение скриптов

### Выполнение скриптов

#### POST `/api/v1/scripts/{script_path}`

Выполняет Python скрипт по указанному логическому пути.

**Требования к скрипту:**
- Должен быть одним файлом `.py`
- Должен содержать функцию `main(data: dict) -> dict`
- Функция получает JSON данные как словарь
- Функция должна возвращать словарь (или `None`, что станет пустым `{}`)

**Параметры:**
- `script_path` (path): Логический путь к скрипту (например, `geology/analysis.py` или `test_script.py` для скрипта в корне)

**Примечание:** `script_path` соответствует полю `logical_path` из системы управления скриптами. Это позволяет выполнять скрипты, организованные в папки, используя их логический путь.

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
│   ├── database.py                  # Настройка базы данных
│   ├── auth/                        # Модуль аутентификации
│   │   ├── models.py                # Модели пользователей
│   │   ├── router.py                # Эндпойнты регистрации/входа
│   │   ├── service.py               # Сервис аутентификации (JWT)
│   │   ├── schemas.py               # Схемы для аутентификации
│   │   └── dependencies.py          # Зависимости для проверки токенов
│   ├── scripts_manager/             # Модуль управления скриптами и папками
│   │   ├── models.py                # Модели папок и скриптов
│   │   ├── router.py                # Эндпойнты управления скриптами/папками
│   │   ├── service.py               # Бизнес-логика управления
│   │   ├── schemas.py               # Схемы запросов/ответов
│   │   ├── validators.py            # Валидация скриптов (проверка main())
│   │   ├── error_codes.py           # Коды ошибок
│   │   ├── exceptions.py            # Кастомные исключения
│   │   ├── error_handler.py         # Обработка ошибок
│   │   └── API_DOCUMENTATION.md     # Подробная документация API
│   ├── file_storage/
│   │   ├── __init__.py              # Экспорт классов
│   │   ├── client.py                # Протокол и LocalFileStorage
│   │   ├── router.py                # Эндпойнты для файлов
│   │   └── schemas.py               # Схемы для файлового API
│   └── script_executor/
│       ├── router.py                # Эндпойнт выполнения скриптов
│       ├── service.py               # Сервис выполнения (через main())
│       └── schemas.py               # Схемы запросов/ответов
├── scripts/                         # Директория со скриптами (физическое хранилище)
│   └── [скрипты хранятся здесь с уникальными именами]
├── uploads/                         # Локальное файловое хранилище
├── scripts_manager.db               # SQLite база данных (структура папок и метаданные)
├── pyproject.toml                   # Зависимости проекта
└── README.md                        # Документация
```

**Важно:** Структура папок и скриптов управляется через базу данных, а не через файловую систему. Все скрипты физически хранятся в корне директории `scripts/`, а логическая иерархия (папки) хранится в базе данных.

## Безопасность

- ✅ **Аутентификация и авторизация** — JWT токены, проверка прав доступа
- ✅ **Контроль доступа к ресурсам** — только владельцы и администраторы могут редактировать/удалять
- ✅ **Валидация путей скриптов** (защита от path traversal)
- ✅ **Валидация содержимого скриптов** — проверка наличия функции `main()`
- ✅ **Ограничение времени выполнения скриптов**
- ✅ **Ограничение размера загружаемых файлов**
- ✅ **Проверка расширений файлов**
- ✅ **Изоляция выполнения скриптов** (subprocess)
- ✅ **Генерация уникальных имен файлов** (избежание коллизий)
- ✅ **Единый формат ошибок** — не раскрывает внутреннюю структуру системы

## Конфигурация

Настройки можно изменить в `src/config.py` или через переменные окружения:

- `SCRIPTS_DIR` - директория со скриптами (по умолчанию `./scripts`)
- `UPLOADS_DIR` - директория для файлового хранилища (по умолчанию `./uploads`)
- `DATABASE_URL` - URL базы данных (по умолчанию SQLite: `sqlite+aiosqlite:///./scripts_manager.db`)
- `JWT_SECRET_KEY` - секретный ключ для JWT токенов (обязательно для production)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - время жизни токена (по умолчанию 30 минут)
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

### Пример 2: Управление скриптами через API

**Шаг 1: Регистрация и вход**
```bash
# Регистрация
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"login": "developer", "password": "secure_pass"}'

# Вход
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "developer", "password": "secure_pass"}' | jq -r '.access_token')
```

**Шаг 2: Создание папки и загрузка скрипта**
```bash
# Создать папку
curl -X POST "http://localhost:8000/api/v1/scripts-manager/folders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my_scripts", "parent_id": null}'

# Загрузить скрипт в папку
curl -X POST "http://localhost:8000/api/v1/scripts-manager/scripts" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@my_script.py" \
  -F "display_name=My Script" \
  -F "description=Test script" \
  -F "folder_id=1" \
  -F "replace=false"
```

**Шаг 3: Получение дерева структуры**
```bash
curl "http://localhost:8000/api/v1/scripts-manager/tree" \
  -H "Authorization: Bearer $TOKEN"
```

**Шаг 4: Выполнение скрипта по логическому пути**
```bash
curl -X POST "http://localhost:8000/api/v1/scripts/my_scripts/my_script.py" \
  -H "Content-Type: application/json" \
  -d '{"data": {"key": "value"}}'
```

### Пример 3: Работа с файлами

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

**Через API (рекомендуется):**

1. Получите JWT токен через `/api/v1/auth/login`
2. Создайте папку (опционально) через `POST /api/v1/scripts-manager/folders`
3. Загрузите скрипт через `POST /api/v1/scripts-manager/scripts` с файлом и метаданными
4. Выполните скрипт через `POST /api/v1/scripts/{logical_path}`

**Вручную (для разработки):**

1. Создайте файл в директории `scripts/` (например, `scripts/my_script.py`)
2. Напишите функцию `main(data: dict) -> dict`
3. Вызовите скрипт через API: `POST /api/v1/scripts/my_script.py`

**Примечание:** Скрипты, добавленные вручную, не будут видны в системе управления скриптами до тех пор, пока не будут загружены через API.

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

### Использование другой базы данных

По умолчанию используется SQLite. Для использования PostgreSQL или MySQL:

1. Установите соответствующий драйвер (например, `asyncpg` для PostgreSQL)
2. Измените `DATABASE_URL` в конфигурации:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
   ```
3. Убедитесь, что база данных создана и доступна

## Дополнительная документация

- **[API Documentation](./src/scripts_manager/API_DOCUMENTATION.md)** — полная документация всех эндпойнтов управления скриптами и папками для фронтенд-разработчиков
- **Swagger UI** — интерактивная документация API: http://localhost:8000/docs
- **ReDoc** — альтернативная документация API: http://localhost:8000/redoc

## Лицензия

MIT
