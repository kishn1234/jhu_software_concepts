"""Entry point for the containerized Flask web service."""

# pylint: disable=import-error

from app.flask_app import create_app


application = create_app()


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)
