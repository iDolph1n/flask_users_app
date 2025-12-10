from flask import request


def get_client_ip() -> str | None:
    """Получить IP клиента (с учётом X-Forwarded-For за прокси)."""
    if "X-Forwarded-For" in request.headers:
        # Берём первый IP из списка
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr


def normalize_str(value: str | None) -> str | None:
    """Простая нормализация строк: trim + None вместо пустой строки."""
    if value is None:
        return None
    value = value.strip()
    return value or None
