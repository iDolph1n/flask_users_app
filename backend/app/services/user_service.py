from typing import List, Tuple, Optional, Dict, Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.user import User
from app.extensions import db
from app.utils.exceptions import (
    NotFoundException,
    ConflictException,
    DatabaseException,
)


class UserService:
    """Сервис для работы с пользователями (бизнес-логика)."""

    @staticmethod
    def get_all_users(
            page: int = 1,
            per_page: int = 20,
            search: Optional[str] = None,
    ) -> Tuple[List[User], Dict[str, Any]]:
        """
        Получить всех пользователей с пагинацией и опциональным поиском.
        """
        try:
            query = User.query.filter_by(is_active=True)

            # Поиск по имени или email
            if search and search.strip():
                search_pattern = f"%{search.strip()}%"
                query = query.filter(
                    db.or_(
                        User.name.ilike(search_pattern),
                        User.email.ilike(search_pattern),
                    )
                )

            # Сортировка по дате создания (новые сверху) и пагинация
            paginated = query.order_by(User.created_at.desc()).paginate(
                page=page,
                per_page=per_page,
                error_out=False,
            )

            metadata: Dict[str, Any] = {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            }

            return list(paginated.items), metadata

        except SQLAlchemyError as e:
            raise DatabaseException(f"Ошибка при получении пользователей: {str(e)}")

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Получить пользователя по ID."""
        user = User.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"Пользователь с ID {user_id} не найден")
        return user

    @staticmethod
    def create_user(name: str, email: str) -> User:
        """Создать нового пользователя."""
        try:
            # Нормализация
            name = name.strip()
            email = email.strip().lower()

            # Проверка существования
            existing = User.find_by_email(email)
            if existing:
                raise ConflictException(
                    f"Пользователь с email {email} уже существует",
                )

            # Создание
            user = User(name=name, email=email, is_active=True)
            db.session.add(user)
            db.session.commit()
            return user

        except ConflictException:
            # Перебрасываем специализированное исключение как есть
            raise
        except IntegrityError:
            db.session.rollback()
            raise ConflictException(f"Email {email} уже используется")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseException(f"Ошибка создания пользователя: {str(e)}")

    @staticmethod
    def update_user(user_id: int, **kwargs) -> User:
        """Обновить пользователя (частичное обновление)."""
        try:
            user = UserService.get_user_by_id(user_id)

            # Обновляем только переданные поля
            for key, value in kwargs.items():
                if not hasattr(user, key) or value is None:
                    continue

                if key == "email":
                    value = value.strip().lower()
                elif key == "name":
                    value = value.strip()

                setattr(user, key, value)

            db.session.commit()
            return user

        except ConflictException:
            raise
        except IntegrityError:
            db.session.rollback()
            raise ConflictException("Email уже используется другим пользователем")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseException(f"Ошибка обновления: {str(e)}")

    @staticmethod
    def delete_user(user_id: int, soft_delete: bool = True) -> None:
        """Удалить пользователя (мягкое или жёсткое удаление)."""
        try:
            user = UserService.get_user_by_id(user_id)

            if soft_delete:
                # Мягкое удаление
                user.is_active = False
                db.session.commit()
            else:
                # Жёсткое удаление
                db.session.delete(user)
                db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseException(f"Ошибка удаления: {str(e)}")
