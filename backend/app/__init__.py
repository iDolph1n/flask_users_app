import os

from app.config import config
from app.extensions import init_extensions, db
from app.utils.exceptions import AppException
from flask import Flask, jsonify, render_template


def create_app(config_name: str | None = None) -> Flask:
    """
    Application Factory Pattern.
    """

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    # Загрузка конфигурации
    app.config.from_object(config.get(config_name, config["default"]))

    # Строгая проверка только если действительно выбран production
    if config_name == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in production configuration")

    # Инициализация расширений (db, migrate, cors и т.д.)
    init_extensions(app)

    # Регистрация blueprints
    register_blueprints(app)

    # Регистрация обработчиков ошибок
    register_error_handlers(app)

    @app.route("/")
    def index_page():
        return render_template("index.html")

    # Инициализация БД (для разработки/тестов можно использовать create_all,
    # в проде полагаться на Alembic миграции)
    with app.app_context():
        if config_name in ("development", "testing"):
            db.create_all()
            if config_name == "development":
                seed_database()

    return app


def register_blueprints(app: Flask) -> None:
    """Регистрация всех blueprints приложения."""
    from app.routes import users

    app.register_blueprint(users.bp)


def register_error_handlers(app: Flask) -> None:
    """Регистрация глобальных обработчиков ошибок."""

    @app.errorhandler(AppException)
    def handle_app_exception(error: AppException):
        response = jsonify(
            {
                "success": False,
                **error.to_dict(),
            }
        )
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Ресурс не найден",
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        # На всякий случай откатим сессию при ошибке БД
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Внутренняя ошибка сервера",
                }
            ),
            500,
        )


def seed_database() -> None:
    """Добавление тестовых данных для разработки."""
    from app.models.user import User

    if User.query.count() > 0:
        return

    test_users = [
        {"name": "Иван Иванов", "email": "ivan@example.com"},
        {"name": "Мария Петрова", "email": "maria@example.com"},
        {"name": "Алексей Сидоров", "email": "alexey@example.com"},
        {"name": "Елена Смирнова", "email": "elena@example.com"},
        {"name": "Дмитрий Козлов", "email": "dmitry@example.com"},
    ]

    for user_data in test_users:
        user = User(**user_data)
        db.session.add(user)

    db.session.commit()
    print("✅ Тестовые пользователи добавлены")
