from datetime import datetime, UTC

from app.extensions import db


class User(db.Model):
    """Модель пользователя (SQLAlchemy ORM)."""

    __tablename__ = "users"

    # Столбцы
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Индексы
    __table_args__ = (
        db.Index("ix_users_email_active", "email", "is_active"),
        db.Index("ix_users_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        """Сериализация в словарь (при необходимости)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
        }

    # Утилиты для поиска
    @classmethod
    def find_by_id(cls, user_id: int) -> "User | None":
        """Найти пользователя по ID (только активных)."""
        return cls.query.filter_by(id=user_id, is_active=True).first()

    @classmethod
    def find_by_email(cls, email: str) -> "User | None":
        """Найти пользователя по email (только активных)."""
        return (
            cls.query.filter_by(email=email.lower().strip(), is_active=True).first()
        )
