def helper_function(value: int) -> int:
    """Функция удваивает число"""
    return value * 2

def main(data: dict) -> dict:
    """Главная функция, в которую передаются данные, которые посылает пользователь"""
    name: str = data.get("name", "Noname")
    value: int = int(data.get("value", 0))
    new_value: int = helper_function(value)
    return {"message": f"Привет, господин {name}",
            "new_value": new_value}