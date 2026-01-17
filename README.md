# Scripts Manager

REST API сервис для выполнения Python скриптов с гибкой передачей данных.

## Описание

Scripts Manager позволяет выполнять Python скрипты через REST API, передавая данные в различных форматах (JSON, файлы, параметры). Сервис разработан для интеграции с ПО для гидродинамического моделирования, где Python интерпретатор имеет ограниченный набор библиотек.

## Основные возможности

- ✅ Выполнение Python скриптов через REST API
- ✅ Гибкая передача данных (JSON, файлы, параметры)
- ✅ Безопасное выполнение скриптов (валидация путей, таймауты)
- ✅ Автоматическая очистка временных файлов
- ✅ Детальное логирование

## Установка

```bash
# Установка зависимостей
pip install -e .

# Или через uv
uv pip install -e .
```

## Запуск

```bash
# Запуск сервера разработки
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Или через Python
python -m uvicorn src.app:app --reload
```

После запуска документация API доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST `/api/v1/scripts/{script_path}`

Выполняет Python скрипт по указанному пути.

**Параметры:**
- `script_path` (path): Относительный путь к скрипту от папки `scripts/`
- `json_data` (form, optional): JSON данные в виде строки
- `params` (form, optional): Дополнительные параметры в виде JSON строки
- `files` (form, optional): Загружаемые файлы

**Пример запроса с JSON данными:**

```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_args_in_request_args_in_response.py" \
  -F 'json_data={"name": "John", "value": 42}'
```

**Пример запроса с файлами:**

```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_file_in_request_file_in_response.py" \
  -F "files=@/path/to/file.txt"
```

**Пример запроса с JSON и файлами:**

```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_args_in_request_file_in_response.py" \
  -F 'json_data={"text": "Hello World", "filename": "output.txt"}'
```

## Как писать скрипты

Скрипты получают входные данные через глобальную переменную `INPUT_DATA`:

```python
# Доступ к входным данным
input_data = globals().get("INPUT_DATA", {})

# JSON данные и параметры
name = input_data.get("name", "Unknown")
value = input_data.get("value", 0)

# Загруженные файлы
files = input_data.get("_files", {})
# files = {"filename.txt": "/tmp/xyz/filename.txt"}

# Временная директория для файлов
temp_dir = input_data.get("_temp_dir", "/tmp")
```

**Важно:**
- Скрипт должен выводить результат в stdout в формате JSON
- Если результат не JSON, он будет возвращен как строка
- Файлы автоматически сохраняются во временной директории
- Временная директория очищается после выполнения

**Пример скрипта:**

```python
import json

# Получаем входные данные
input_data = globals().get("INPUT_DATA", {})

# Обрабатываем данные
result = {
    "message": f"Hello, {input_data.get('name', 'Unknown')}!",
    "processed": True,
}

# Выводим результат как JSON
print(json.dumps(result))
```

## Структура проекта

```
scripts_manager/
├── src/
│   ├── app.py                 # Главное приложение FastAPI
│   ├── config.py              # Конфигурация
│   ├── logger.py              # Настройка логирования
│   └── script_executor/
│       ├── router.py          # API роутеры
│       ├── service.py         # Логика выполнения скриптов
│       └── schemas.py         # Pydantic схемы
├── scripts/                   # Директория со скриптами
│   ├── test/                  # Тестовые скрипты
│   ├── hydrodynamics/         # Скрипты для гидродинамики
│   └── geology/               # Скрипты для геологии
└── pyproject.toml             # Зависимости проекта
```

## Безопасность

- ✅ Валидация путей скриптов (защита от path traversal)
- ✅ Ограничение времени выполнения скриптов
- ✅ Ограничение размера загружаемых файлов
- ✅ Проверка расширений файлов
- ✅ Изоляция выполнения скриптов

## Конфигурация

Настройки можно изменить в `src/config.py` или через переменные окружения:

- `SCRIPTS_DIR` - директория со скриптами
- `MAX_SCRIPT_EXECUTION_TIME` - максимальное время выполнения (секунды)
- `MAX_FILE_SIZE` - максимальный размер файла (байты)
- `DEBUG` - режим отладки

## Примеры использования

### Пример 1: Передача JSON данных

**Скрипт:** `scripts/test/test_args_in_request_args_in_response.py`

```python
import json
input_data = globals().get("INPUT_DATA", {})
result = {"message": f"Hello, {input_data.get('name')}!"}
print(json.dumps(result))
```

**Запрос:**
```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_args_in_request_args_in_response.py" \
  -F 'json_data={"name": "World"}'
```

### Пример 2: Обработка файлов

**Скрипт:** `scripts/test/test_file_in_request_file_in_response.py`

```python
import json
from pathlib import Path

input_data = globals().get("INPUT_DATA", {})
files = input_data.get("_files", {})

result = {"files_count": len(files)}
print(json.dumps(result))
```

**Запрос:**
```bash
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_file_in_request_file_in_response.py" \
  -F "files=@data.txt"
```

## Разработка

### Добавление нового скрипта

1. Создайте файл в директории `scripts/` (например, `scripts/my_script.py`)
2. Напишите скрипт, используя `INPUT_DATA` для получения входных данных
3. Вызовите скрипт через API: `POST /api/v1/scripts/my_script.py`

### Тестирование

```bash
# Запуск тестовых скриптов
curl -X POST "http://localhost:8000/api/v1/scripts/test/test_args_in_request_args_in_response.py" \
  -F 'json_data={"name": "Test", "value": 123}'
```

## Лицензия

MIT

