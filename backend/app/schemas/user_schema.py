import re

from marshmallow import Schema, fields, validate, validates, ValidationError


class UserSchema(Schema):
    """Основная схема пользователя (для операций чтения)."""

    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=2,
                max=100,
                error="Имя должно быть от 2 до 100 символов",
            )
        ],
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(
            max=120,
            error="Email слишком длинный",
        ),
    )
    created_at = fields.DateTime(dump_only=True, format="iso")
    updated_at = fields.DateTime(dump_only=True, format="iso")
    is_active = fields.Bool(dump_only=True)

    @validates("name")
    def validate_name(self, value: str):
        """Валидация имени (только буквы, пробелы и дефисы)."""
        if not re.match(r"^[а-яА-ЯёЁa-zA-Z\s\-]{2,100}$", value.strip()):
            raise ValidationError(
                "Имя может содержать только буквы, пробелы и дефисы",
            )

    @validates("email")
    def validate_email(self, value: str):
        """Дополнительная валидация email (отсечение временных доменов)."""
        disposable_domains = [
            "tempmail.com",
            "10minutemail.com",
            "guerrillamail.com",
            "maildrop.cc",
        ]
        domain = value.split("@")[1].lower()
        if domain in disposable_domains:
            raise ValidationError("Временные email адреса не разрешены")


class UserCreateSchema(Schema):
    """Схема для создания пользователя."""

    name = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=2,
                max=100,
                error="Имя должно быть от 2 до 100 символов",
            )
        ],
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(
            max=120,
            error="Email слишком длинный",
        ),
    )

    @validates("name")
    def validate_name(self, value: str):
        if not re.match(r"^[а-яА-ЯёЁa-zA-Z\s\-]{2,100}$", value.strip()):
            raise ValidationError(
                "Имя может содержать только буквы, пробелы и дефисы",
            )

    @validates("email")
    def validate_email(self, value: str):
        disposable_domains = [
            "tempmail.com",
            "10minutemail.com",
            "guerrillamail.com",
            "maildrop.cc",
        ]
        domain = value.split("@")[1].lower()
        if domain in disposable_domains:
            raise ValidationError("Временные email адреса не разрешены")


class UserUpdateSchema(Schema):
    """Схема для обновления пользователя (все поля опциональны)."""

    name = fields.Str(
        validate=[
            validate.Length(
                min=2,
                max=100,
                error="Имя должно быть от 2 до 100 символов",
            )
        ],
    )
    email = fields.Email(
        validate=validate.Length(
            max=120,
            error="Email слишком длинный",
        ),
    )

    @validates("name")
    def validate_name(self, value: str):
        if value and not re.match(r"^[а-яА-ЯёЁa-zA-Z\s\-]{2,100}$", value.strip()):
            raise ValidationError(
                "Имя может содержать только буквы, пробелы и дефисы",
            )


class PaginationSchema(Schema):
    """Схема для параметров пагинации."""

    page = fields.Int(
        load_default=1,
        validate=validate.Range(
            min=1,
            error="Номер страницы должен быть >= 1",
        ),
    )
    per_page = fields.Int(
        load_default=20,
        validate=validate.Range(
            min=1,
            max=100,
            error="Размер страницы должен быть от 1 до 100",
        ),
    )
    search = fields.Str(allow_none=True)
