from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Инстансы расширений (создаются один раз, инициализируются в init_extensions)
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


def init_extensions(app):
    """Инициализация всех расширений Flask."""

    # SQLAlchemy
    db.init_app(app)

    # Миграции БД
    migrate.init_app(app, db)

    # CORS (ограничиваем по /api/* и по списку origins из конфигурации)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "max_age": 3600,
            }
        },
    )
