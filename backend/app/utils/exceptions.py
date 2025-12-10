class AppException(Exception):
    """Базовое исключение приложения."""

    status_code = 500

    def __init__(self, message: str, status_code: int | None = None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> dict:
        """Преобразование в JSON‑словарь."""
        rv = dict(self.payload)
        rv["error"] = self.message
        return rv


class ValidationException(AppException):
    """Ошибка валидации входных данных."""

    status_code = 400


class NotFoundException(AppException):
    """Ресурс не найден."""

    status_code = 404


class ConflictException(AppException):
    """Конфликт (например, дубликат email)."""

    status_code = 409


class DatabaseException(AppException):
    """Ошибка базы данных."""

    status_code = 500


class UnauthorizedException(AppException):
    """Не авторизован."""

    status_code = 401


class ForbiddenException(AppException):
    """Доступ запрещен."""

    status_code = 403
