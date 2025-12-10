import os

from dotenv import load_dotenv

from app import create_app

# Загрузка переменных окружения из .env
load_dotenv()

# Выбор конфигурации по FLASK_ENV (development / production / testing)
config_name = os.getenv("FLASK_ENV", "development")

# Создание приложения через фабрику
app = create_app(config_name)


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = app.config.get("DEBUG", False)

    print(
        f"\n"
        f"╔══════════════════════════════════════╗\n"
        f"║ 🚀 Flask User Service                ║\n"
        f"║ Running on http://{host}:{port:<5}           ║\n"
        f"║ Debug: {str(debug).ljust(26)}║\n"
        f"╚══════════════════════════════════════╝\n"
    )

    # В продакшене debug должен быть False, управление лучше отдать gunicorn/uwsgi
    app.run(host=host, port=port, debug=debug)
