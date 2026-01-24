# API Documentation: Scripts Manager

Документация API для управления скриптами и папками. Эта документация предназначена для фронтенд-разработчиков, реализующих пользовательский интерфейс.

## Содержание

1. [Общая информация](#общая-информация)
2. [Аутентификация](#аутентификация)
3. [Формат ошибок](#формат-ошибок)
4. [Эндпойнты для работы с папками](#эндпойнты-для-работы-с-папками)
5. [Эндпойнты для работы со скриптами](#эндпойнты-для-работы-со-скриптами)
6. [Эндпойнт для получения дерева](#эндпойнт-для-получения-дерева)

---

## Общая информация

**Базовый URL:** `/scripts-manager`

Все эндпойнты требуют аутентификации через Bearer токен в заголовке `Authorization`.

**Формат заголовка:**
```
Authorization: Bearer <access_token>
```

---

## Аутентификация

Все эндпойнты требуют аутентификации. Токен должен быть передан в заголовке `Authorization` в формате:
```
Authorization: Bearer <your_access_token>
```

При отсутствии или невалидности токена будет возвращена ошибка `401 Unauthorized`.

---

## Формат ошибок

Все ошибки возвращаются в едином формате:

```json
{
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "key": "value"
  }
}
```

### Поля ответа с ошибкой:

- **error_code** (string, обязательное) - Машинно-читаемый код ошибки. Используйте его для программной обработки ошибок.
- **message** (string, обязательное) - Человеко-читаемое сообщение об ошибке. Может быть показано пользователю.
- **details** (object, опциональное) - Дополнительная информация об ошибке. Содержит контекстные данные (ID ресурсов, пути и т.д.).

### HTTP статус коды:

- **400 Bad Request** - Ошибка валидации входных данных
- **403 Forbidden** - Недостаточно прав для выполнения операции
- **404 Not Found** - Ресурс не найден
- **409 Conflict** - Конфликт (например, ресурс уже существует)
- **500 Internal Server Error** - Внутренняя ошибка сервера

### Коды ошибок:

#### Ошибки валидации (400):
- `VALIDATION_ERROR` - Общая ошибка валидации
- `INVALID_FILENAME` - Некорректное имя файла
- `INVALID_SCRIPT_CONTENT` - Некорректное содержимое скрипта
- `SCRIPT_MISSING_MAIN` - Скрипт не содержит функцию `main`
- `INVALID_FOLDER_NAME` - Некорректное имя папки

#### Ресурс не найден (404):
- `FOLDER_NOT_FOUND` - Папка не найдена
- `SCRIPT_NOT_FOUND` - Скрипт не найден
- `PARENT_FOLDER_NOT_FOUND` - Родительская папка не найдена

#### Конфликты (409):
- `FOLDER_ALREADY_EXISTS` - Папка с таким именем уже существует
- `SCRIPT_ALREADY_EXISTS` - Скрипт с таким именем уже существует
- `SCRIPT_EXISTS_REPLACE_REQUIRED` - Скрипт уже существует, требуется перезапись (используйте `replace=true`)

#### Ошибки прав доступа (403):
- `PERMISSION_DENIED` - Общая ошибка прав доступа
- `NOT_FOLDER_OWNER` - Пользователь не является владельцем папки
- `NOT_SCRIPT_OWNER` - Пользователь не является владельцем скрипта
- `NOT_ALL_OWNER` - Пользователь не является владельцем всех ресурсов в папке (для удаления папки)

#### Внутренние ошибки (500):
- `INTERNAL_ERROR` - Внутренняя ошибка сервера
- `DATABASE_ERROR` - Ошибка базы данных
- `FILE_SYSTEM_ERROR` - Ошибка файловой системы

---

## Эндпойнты для работы с папками

### 1. Создание папки

**POST** `/scripts-manager/folders`

Создает новую папку в системе. Папка может быть создана в корне или внутри другой папки.

#### Запрос

**Тело запроса (JSON):**
```json
{
  "name": "geology",
  "parent_id": null
}
```

**Параметры:**
- `name` (string, обязательное) - Имя папки. Минимум 1 символ, максимум 255 символов.
- `parent_id` (integer | null, опциональное) - ID родительской папки. Если `null` или не указан, папка создается в корне.

#### Успешный ответ (201 Created)

```json
{
  "id": 1,
  "name": "geology",
  "path": "geology",
  "parent_id": null,
  "created_by": {
    "id": 1,
    "login": "user123"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "can_edit": true,
  "can_delete": true
}
```

**Поля ответа:**
- `id` (integer) - Уникальный идентификатор папки
- `name` (string) - Имя папки
- `path` (string) - Полный путь папки (например, "geology" или "geology/analysis")
- `parent_id` (integer | null) - ID родительской папки
- `created_by` (object) - Информация о создателе:
  - `id` (integer) - ID пользователя
  - `login` (string) - Логин пользователя
- `created_at` (string, ISO 8601) - Дата и время создания
- `updated_at` (string, ISO 8601) - Дата и время последнего обновления
- `can_edit` (boolean) - Может ли текущий пользователь редактировать папку
- `can_delete` (boolean) - Может ли текущий пользователь удалять папку

#### Возможные ошибки

**400 Bad Request** - Ошибка валидации:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error message",
  "details": {}
}
```

**404 Not Found** - Родительская папка не найдена:
```json
{
  "error_code": "PARENT_FOLDER_NOT_FOUND",
  "message": "Parent folder with id 999 not found",
  "details": {
    "parent_id": "999"
  }
}
```

**409 Conflict** - Папка с таким именем уже существует:
```json
{
  "error_code": "FOLDER_ALREADY_EXISTS",
  "message": "Folder 'geology' already exists",
  "details": {
    "path": "geology"
  }
}
```

---

### 2. Получение информации о папке

**GET** `/scripts-manager/folders/{folder_id}`

Получает информацию о конкретной папке.

#### Запрос

**Параметры пути:**
- `folder_id` (integer) - ID папки

#### Успешный ответ (200 OK)

```json
{
  "id": 1,
  "name": "geology",
  "path": "geology",
  "parent_id": null,
  "created_by": {
    "id": 1,
    "login": "user123"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "can_edit": true,
  "can_delete": true
}
```

#### Возможные ошибки

**404 Not Found** - Папка не найдена:
```json
{
  "error_code": "FOLDER_NOT_FOUND",
  "message": "Folder with id 999 not found",
  "details": {
    "folder_id": "999"
  }
}
```

---

### 3. Обновление папки (переименование)

**PUT** `/scripts-manager/folders/{folder_id}`

Переименовывает папку. Только владелец папки или администратор могут переименовать папку.

#### Запрос

**Параметры пути:**
- `folder_id` (integer) - ID папки

**Тело запроса (JSON):**
```json
{
  "name": "geology_updated"
}
```

**Параметры:**
- `name` (string, опциональное) - Новое имя папки. Минимум 1 символ, максимум 255 символов.

#### Успешный ответ (200 OK)

```json
{
  "id": 1,
  "name": "geology_updated",
  "path": "geology_updated",
  "parent_id": null,
  "created_by": {
    "id": 1,
    "login": "user123"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "can_edit": true,
  "can_delete": true
}
```

#### Возможные ошибки

**400 Bad Request** - Ошибка валидации:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Validation error message",
  "details": {}
}
```

**403 Forbidden** - Недостаточно прав:
```json
{
  "error_code": "NOT_FOLDER_OWNER",
  "message": "You don't have permission to edit this folder",
  "details": {
    "folder_id": "1"
  }
}
```

**404 Not Found** - Папка не найдена:
```json
{
  "error_code": "FOLDER_NOT_FOUND",
  "message": "Folder with id 999 not found",
  "details": {
    "folder_id": "999"
  }
}
```

**409 Conflict** - Папка с таким именем уже существует:
```json
{
  "error_code": "FOLDER_ALREADY_EXISTS",
  "message": "Folder 'geology_updated' already exists",
  "details": {
    "path": "geology_updated"
  }
}
```

---

### 4. Удаление папки

**DELETE** `/scripts-manager/folders/{folder_id}`

Удаляет папку и все её содержимое (подпапки и скрипты). Папку может удалить только:
- Владелец папки, если он является владельцем всех подпапок и скриптов внутри
- Администратор

**Внимание:** Операция необратима. Все скрипты и подпапки будут удалены.

#### Запрос

**Параметры пути:**
- `folder_id` (integer) - ID папки

#### Успешный ответ (204 No Content)

Тело ответа отсутствует.

#### Возможные ошибки

**403 Forbidden** - Недостаточно прав:
```json
{
  "error_code": "NOT_ALL_OWNER",
  "message": "You don't have permission to delete this folder",
  "details": {
    "folder_id": "1"
  }
}
```

**404 Not Found** - Папка не найдена:
```json
{
  "error_code": "FOLDER_NOT_FOUND",
  "message": "Folder with id 999 not found",
  "details": {
    "folder_id": "999"
  }
}
```

---

## Эндпойнты для работы со скриптами

### 1. Создание скрипта

**POST** `/scripts-manager/scripts`

Загружает новый скрипт в систему. Скрипт может быть размещен в корне или в папке.

**Важно:** Скрипт должен содержать функцию `main(data: dict) -> dict`. Эта функция будет вызываться при выполнении скрипта.

#### Запрос

**Content-Type:** `multipart/form-data`

**Параметры формы:**
- `file` (file, обязательное) - Файл скрипта с расширением `.py`
- `display_name` (string, обязательное) - Отображаемое имя скрипта. Минимум 1 символ, максимум 255 символов.
- `description` (string, опциональное) - Описание скрипта
- `folder_id` (integer, опциональное) - ID папки, в которую поместить скрипт. Если не указан, скрипт размещается в корне.
- `replace` (boolean, опциональное, по умолчанию `false`) - Если `true`, перезаписывает существующий скрипт с таким же логическим путем в той же папке.

**Пример запроса (FormData):**
```
file: [File object: script.py]
display_name: "Analysis Script"
description: "Script for data analysis"
folder_id: 1
replace: false
```

#### Успешный ответ (201 Created)

```json
{
  "id": 1,
  "filename": "script.py",
  "logical_path": "geology/script.py",
  "display_name": "Analysis Script",
  "description": "Script for data analysis",
  "folder_id": 1,
  "created_by": {
    "id": 1,
    "login": "user123"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "can_edit": true,
  "can_delete": true
}
```

**Поля ответа:**
- `id` (integer) - Уникальный идентификатор скрипта
- `filename` (string) - Имя файла скрипта (оригинальное имя)
- `logical_path` (string) - Логический путь для выполнения (например, "geology/script.py"). Используется для удаленного запуска скрипта.
- `display_name` (string) - Отображаемое имя скрипта
- `description` (string | null) - Описание скрипта
- `folder_id` (integer | null) - ID папки, в которой находится скрипт
- `created_by` (object) - Информация о создателе
- `created_at` (string, ISO 8601) - Дата и время создания
- `updated_at` (string, ISO 8601) - Дата и время последнего обновления
- `can_edit` (boolean) - Может ли текущий пользователь редактировать скрипт
- `can_delete` (boolean) - Может ли текущий пользователь удалять скрипт

#### Возможные ошибки

**400 Bad Request** - Ошибка валидации:

Нет имени файла:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Filename is required",
  "details": {}
}
```

Некорректное расширение файла:
```json
{
  "error_code": "INVALID_FILENAME",
  "message": "File must have .py extension",
  "details": {
    "filename": "script.txt"
  }
}
```

Скрипт не содержит функцию `main`:
```json
{
  "error_code": "SCRIPT_MISSING_MAIN",
  "message": "Script validation failed: Script must contain a 'main(data: dict) -> dict' function",
  "details": {
    "error_code": "SCRIPT_MISSING_MAIN"
  }
}
```

Некорректное содержимое скрипта:
```json
{
  "error_code": "INVALID_SCRIPT_CONTENT",
  "message": "Script validation failed: ...",
  "details": {
    "error_code": "INVALID_SCRIPT_CONTENT"
  }
}
```

**403 Forbidden** - Недостаточно прав для перезаписи:
```json
{
  "error_code": "NOT_SCRIPT_OWNER",
  "message": "You don't have permission to replace this script",
  "details": {
    "script_id": "1"
  }
}
```

**404 Not Found** - Папка не найдена:
```json
{
  "error_code": "FOLDER_NOT_FOUND",
  "message": "Folder with id 999 not found",
  "details": {
    "folder_id": "999"
  }
}
```

**409 Conflict** - Скрипт уже существует (требуется перезапись):

**Важно:** Это специальный случай для обработки на фронтенде. Когда пользователь пытается загрузить скрипт, который уже существует, фронтенд должен:
1. Проверить `error_code === "SCRIPT_EXISTS_REPLACE_REQUIRED"`
2. Показать диалог подтверждения перезаписи
3. Если пользователь согласен, повторить запрос с `replace=true`

```json
{
  "error_code": "SCRIPT_EXISTS_REPLACE_REQUIRED",
  "message": "Script 'geology/script.py' already exists. Use replace=True to replace it.",
  "details": {
    "logical_path": "geology/script.py",
    "script_id": "1"
  }
}
```

---

### 2. Получение информации о скрипте

**GET** `/scripts-manager/scripts/{script_id}`

Получает информацию о конкретном скрипте.

#### Запрос

**Параметры пути:**
- `script_id` (integer) - ID скрипта

#### Успешный ответ (200 OK)

```json
{
  "id": 1,
  "filename": "script.py",
  "logical_path": "geology/script.py",
  "display_name": "Analysis Script",
  "description": "Script for data analysis",
  "folder_id": 1,
  "created_by": {
    "id": 1,
    "login": "user123"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "can_edit": true,
  "can_delete": true
}
```

#### Возможные ошибки

**404 Not Found** - Скрипт не найден:
```json
{
  "error_code": "SCRIPT_NOT_FOUND",
  "message": "Script with id 999 not found",
  "details": {
    "script_id": "999"
  }
}
```

---

### 3. Получение содержимого скрипта

**GET** `/scripts-manager/scripts/{script_id}/content`

Получает исходный код скрипта.

#### Запрос

**Параметры пути:**
- `script_id` (integer) - ID скрипта

#### Успешный ответ (200 OK)

```json
{
  "content": "def main(data: dict) -> dict:\n    return {\"result\": \"success\"}\n"
}
```

**Поля ответа:**
- `content` (string) - Исходный код скрипта

#### Возможные ошибки

**404 Not Found** - Скрипт не найден или файл отсутствует:
```json
{
  "error_code": "SCRIPT_NOT_FOUND",
  "message": "Script with id 999 not found",
  "details": {
    "script_id": "999"
  }
}
```

---

### 4. Обновление скрипта

**PUT** `/scripts-manager/scripts/{script_id}`

Обновляет метаданные скрипта (отображаемое имя, описание) или переименовывает скрипт. Только владелец скрипта или администратор могут обновлять скрипт.

**Примечание:** Для изменения содержимого скрипта используйте создание скрипта с `replace=true`.

#### Запрос

**Параметры пути:**
- `script_id` (integer) - ID скрипта

**Тело запроса (JSON):**
```json
{
  "display_name": "Updated Script Name",
  "description": "Updated description",
  "filename": "updated_script.py"
}
```

**Параметры (все опциональные):**
- `display_name` (string, опциональное) - Новое отображаемое имя. Минимум 1 символ, максимум 255 символов.
- `description` (string, опциональное) - Новое описание
- `filename` (string, опциональное) - Новое имя файла. Должно иметь расширение `.py`. При изменении имени файла изменяется `logical_path`.

#### Успешный ответ (200 OK)

```json
{
  "id": 1,
  "filename": "updated_script.py",
  "logical_path": "geology/updated_script.py",
  "display_name": "Updated Script Name",
  "description": "Updated description",
  "folder_id": 1,
  "created_by": {
    "id": 1,
    "login": "user123"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "can_edit": true,
  "can_delete": true
}
```

#### Возможные ошибки

**400 Bad Request** - Ошибка валидации:

Некорректное расширение файла:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Script filename must have .py extension",
  "details": {
    "filename": "script.txt"
  }
}
```

**403 Forbidden** - Недостаточно прав:
```json
{
  "error_code": "NOT_SCRIPT_OWNER",
  "message": "You don't have permission to edit this script",
  "details": {
    "script_id": "1"
  }
}
```

**404 Not Found** - Скрипт не найден:
```json
{
  "error_code": "SCRIPT_NOT_FOUND",
  "message": "Script with id 999 not found",
  "details": {
    "script_id": "999"
  }
}
```

**409 Conflict** - Скрипт с таким именем уже существует:
```json
{
  "error_code": "SCRIPT_ALREADY_EXISTS",
  "message": "Script 'geology/updated_script.py' already exists",
  "details": {
    "logical_path": "geology/updated_script.py"
  }
}
```

---

### 5. Удаление скрипта

**DELETE** `/scripts-manager/scripts/{script_id}`

Удаляет скрипт. Только владелец скрипта или администратор могут удалять скрипт.

**Внимание:** Операция необратима.

#### Запрос

**Параметры пути:**
- `script_id` (integer) - ID скрипта

#### Успешный ответ (204 No Content)

Тело ответа отсутствует.

#### Возможные ошибки

**403 Forbidden** - Недостаточно прав:
```json
{
  "error_code": "NOT_SCRIPT_OWNER",
  "message": "You don't have permission to delete this script",
  "details": {
    "script_id": "1"
  }
}
```

**404 Not Found** - Скрипт не найден:
```json
{
  "error_code": "SCRIPT_NOT_FOUND",
  "message": "Script with id 999 not found",
  "details": {
    "script_id": "999"
  }
}
```

---

## Эндпойнт для получения дерева

### Получение дерева скриптов и папок

**GET** `/scripts-manager/tree`

Получает полную иерархию всех папок и скриптов в системе с информацией о правах доступа для текущего пользователя.

#### Запрос

Параметры не требуются.

#### Успешный ответ (200 OK)

```json
{
  "root_scripts": [
    {
      "id": 1,
      "filename": "root_script.py",
      "logical_path": "root_script.py",
      "display_name": "Root Script",
      "description": "Script in root",
      "folder_id": null,
      "created_by": {
        "id": 1,
        "login": "user123"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "can_edit": true,
      "can_delete": true
    }
  ],
  "root_folders": [
    {
      "folder": {
        "id": 1,
        "name": "geology",
        "path": "geology",
        "parent_id": null,
        "created_by": {
          "id": 1,
          "login": "user123"
        },
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "can_edit": true,
        "can_delete": true
      },
      "scripts": [
        {
          "id": 2,
          "filename": "analysis.py",
          "logical_path": "geology/analysis.py",
          "display_name": "Analysis Script",
          "description": "Analysis script",
          "folder_id": 1,
          "created_by": {
            "id": 1,
            "login": "user123"
          },
          "created_at": "2024-01-15T10:30:00Z",
          "updated_at": "2024-01-15T10:30:00Z",
          "can_edit": true,
          "can_delete": true
        }
      ],
      "subfolders": [
        {
          "folder": {
            "id": 2,
            "name": "subfolder",
            "path": "geology/subfolder",
            "parent_id": 1,
            "created_by": {
              "id": 1,
              "login": "user123"
            },
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "can_edit": true,
            "can_delete": true
          },
          "scripts": [],
          "subfolders": []
        }
      ]
    }
  ]
}
```

**Структура ответа:**
- `root_scripts` (array) - Массив скриптов в корне
- `root_folders` (array) - Массив папок в корне. Каждая папка содержит:
  - `folder` (object) - Информация о папке (формат как в `FolderResponse`)
  - `scripts` (array) - Массив скриптов в этой папке (формат как в `ScriptResponse`)
  - `subfolders` (array) - Массив подпапок (рекурсивная структура `FolderTreeItem`)

**Использование на фронтенде:**
Этот эндпойнт предназначен для построения дерева файлов и папок в UI. Используйте рекурсивную структуру `subfolders` для отображения вложенных папок.

#### Возможные ошибки

Ошибки не ожидаются для этого эндпойнта (требуется аутентификация).

---

## Примеры использования

### Пример 1: Создание папки и загрузка скрипта

```javascript
// 1. Создать папку
const createFolderResponse = await fetch('/scripts-manager/folders', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'geology',
    parent_id: null
  })
});

const folder = await createFolderResponse.json();

// 2. Загрузить скрипт в папку
const formData = new FormData();
formData.append('file', scriptFile); // File object
formData.append('display_name', 'Analysis Script');
formData.append('description', 'Script for data analysis');
formData.append('folder_id', folder.id);
formData.append('replace', 'false');

const createScriptResponse = await fetch('/scripts-manager/scripts', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

if (createScriptResponse.status === 409) {
  const error = await createScriptResponse.json();
  if (error.error_code === 'SCRIPT_EXISTS_REPLACE_REQUIRED') {
    // Показать диалог подтверждения
    const shouldReplace = confirm('Script already exists. Replace?');
    if (shouldReplace) {
      formData.set('replace', 'true');
      const replaceResponse = await fetch('/scripts-manager/scripts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      // Обработать ответ
    }
  }
} else {
  const script = await createScriptResponse.json();
  // Обработать успешное создание
}
```

### Пример 2: Получение дерева и отображение

```javascript
const treeResponse = await fetch('/scripts-manager/tree', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const tree = await treeResponse.json();

// Рекурсивная функция для отображения дерева
function renderTree(folderItem, level = 0) {
  const indent = '  '.repeat(level);
  
  if (folderItem.folder) {
    console.log(`${indent}📁 ${folderItem.folder.name} (${folderItem.folder.path})`);
    
    // Отобразить скрипты в папке
    folderItem.scripts.forEach(script => {
      console.log(`${indent}  📄 ${script.display_name} (${script.logical_path})`);
    });
    
    // Рекурсивно отобразить подпапки
    folderItem.subfolders.forEach(subfolder => {
      renderTree(subfolder, level + 1);
    });
  }
}

// Отобразить скрипты в корне
tree.root_scripts.forEach(script => {
  console.log(`📄 ${script.display_name} (${script.logical_path})`);
});

// Отобразить папки
tree.root_folders.forEach(folder => {
  renderTree(folder);
});
```

### Пример 3: Обработка ошибок

```javascript
async function createScript(scriptFile, displayName, folderId) {
  const formData = new FormData();
  formData.append('file', scriptFile);
  formData.append('display_name', displayName);
  if (folderId) {
    formData.append('folder_id', folderId);
  }
  
  try {
    const response = await fetch('/scripts-manager/scripts', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      switch (error.error_code) {
        case 'SCRIPT_EXISTS_REPLACE_REQUIRED':
          // Показать диалог перезаписи
          return handleReplaceDialog(error);
          
        case 'INVALID_FILENAME':
          alert(`Invalid filename: ${error.message}`);
          break;
          
        case 'SCRIPT_MISSING_MAIN':
          alert('Script must contain a main() function');
          break;
          
        case 'FOLDER_NOT_FOUND':
          alert(`Folder not found: ${error.details.folder_id}`);
          break;
          
        case 'NOT_SCRIPT_OWNER':
          alert('You do not have permission to replace this script');
          break;
          
        default:
          alert(`Error: ${error.message}`);
      }
      
      return null;
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('Network error:', error);
    alert('Network error occurred');
    return null;
  }
}
```

---

## Примечания для разработчиков

1. **Логический путь (`logical_path`)**: Используется для удаленного выполнения скрипта через API выполнения скриптов. Это путь относительно корня системы скриптов (например, "geology/analysis.py").

2. **Права доступа (`can_edit`, `can_delete`)**: Эти поля указывают, может ли текущий пользователь редактировать/удалять ресурс. Используйте их для отображения/скрытия кнопок в UI.

3. **Перезапись скриптов**: При загрузке скрипта, который уже существует, API возвращает ошибку `SCRIPT_EXISTS_REPLACE_REQUIRED`. Фронтенд должен обработать это и предложить пользователю перезаписать скрипт.

4. **Удаление папок**: При удалении папки проверяется, что пользователь является владельцем всех подпапок и скриптов внутри. Если это не так, операция будет отклонена.

5. **Валидация скриптов**: Все скрипты должны содержать функцию `main(data: dict) -> dict`. Эта функция будет вызываться при выполнении скрипта.

6. **Формат дат**: Все даты возвращаются в формате ISO 8601 (например, "2024-01-15T10:30:00Z").

---

## Версия документации

Версия: 1.0  
Дата последнего обновления: 2026-01-24

