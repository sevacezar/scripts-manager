"""
Пример вызова скрипта на сервере через HTTP API из тНавигатор.

Этот пример демонстрирует, как выполнить скрипт на сервере,
используя встроенную библиотеку http.client.
"""

import http.client
import json
from typing import Any


def execute_script(
    host: str,
    port: int,
    script_path: str,
    data: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Выполнить скрипт на сервере.
    
    Args:
        host: Хост сервера (например, 'localhost')
        port: Порт сервера (например, 8000)
        script_path: Логический путь к скрипту (например, 'geology/test.py')
        data: Данные для передачи в скрипт (JSON-сериализуемый словарь)
        
    Returns:
        Словарь с результатом выполнения:
        {
            'success': bool,
            'result': dict | None,
            'error': str | None,
            'execution_time': float
        }
        
    Raises:
        Exception: При ошибках соединения или выполнения запроса
    """
    # Подготовка данных (если не переданы, используем пустой словарь)
    if data is None:
        data = {}
    
    # Создание соединения
    conn = http.client.HTTPConnection(host, port)
    
    try:
        # Формирование пути к эндпоинту
        # API префикс: /api/v1
        # Эндпоинт: /scripts/{script_path}
        path = f"/api/v1/scripts/{script_path}"
        
        # Подготовка заголовков
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Сериализация данных в JSON
        json_data = json.dumps(data, ensure_ascii=False)
        
        # Выполнение POST запроса
        conn.request('POST', path, body=json_data, headers=headers)
        
        # Получение ответа
        response = conn.getresponse()
        
        # Чтение тела ответа
        response_body = response.read().decode('utf-8')
        
        # Проверка статуса ответа
        if response.status == 200:
            # Успешный ответ - парсим JSON
            result = json.loads(response_body)
            return result
        else:
            # Ошибка - пытаемся распарсить JSON с ошибкой
            try:
                error_data = json.loads(response_body)
                error_message = error_data.get('detail', f'HTTP {response.status}')
            except json.JSONDecodeError:
                error_message = f'HTTP {response.status}: {response_body}'
            
            raise Exception(f'Ошибка выполнения скрипта: {error_message}')
            
    finally:
        # Закрытие соединения
        conn.close()


# Пример использования
# Параметры подключения
host = '10.7.115.8'
port = 8000
script_path = 'test/test.py'

# Данные для передачи в скрипт
script_data = {
    'name': 'Тест',
    'value': 42,
}

try:
    # Выполнение скрипта
    result = execute_script(
        host=host,
        port=port,
        script_path=script_path,
        data=script_data
    )
    
    # Обработка результата
    if result.get('success'):
        print('Скрипт выполнен успешно!')
        print(f'Результат: {result.get("result")}')
        print(f'Время выполнения: {result.get("execution_time"):.3f} сек')
    else:
        print(f'Ошибка выполнения скрипта: {result.get("error")}')
        print(f'Время выполнения: {result.get("execution_time"):.3f} сек')
        
except Exception as e:
    print(f'Ошибка: {e}')

